import logging

from django.conf import settings
from django.db.models import Case
from django.db.models import IntegerField
from django.db.models import Value
from django.db.models import When
from django.urls import reverse
from django.utils import timezone
from guardian.shortcuts import assign_perm

from sandwich.core.models.email import EmailType
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.role import RoleName
from sandwich.core.models.task import ACTIVE_TASK_STATUSES
from sandwich.core.models.task import TERMINAL_TASK_STATUSES
from sandwich.core.models.task import Task
from sandwich.core.models.task import TaskStatus
from sandwich.core.service.email_service import send_templated_email
from sandwich.core.service.invitation_service import find_or_create_patient_invitation

logger = logging.getLogger(__name__)


def cancel_task(task: Task) -> None:
    """Cancel a pending task."""
    logger.info(
        "Cancelling task",
        extra={
            "task_id": task.id,
            "patient_id": task.patient.id,
            "organization_id": getattr(task.patient.organization, "id", "unknown"),
        },
    )

    assert task.active, "Task is not active"
    task.status = TaskStatus.CANCELLED
    task.ended_at = timezone.now()
    task.save()

    logger.info("Task cancelled successfully", extra={"task_id": task.id, "patient_id": task.patient.id})


def complete_task(task: Task) -> None:
    """Complete a task."""
    logger.info(
        "Completing task",
        extra={
            "task_id": task.id,
            "patient_id": task.patient.id,
            "organization_id": getattr(task.patient.organization, "id", "unknown"),
        },
    )

    assert task.active, "Task is not active"
    task.status = TaskStatus.COMPLETED
    task.ended_at = timezone.now()
    task.save()

    logger.info("Task completed successfully", extra={"task_id": task.id, "patient_id": task.patient.id})


def send_task_added_email(task: Task) -> None:
    logger.info(
        "Preparing task notification email",
        extra={
            "task_id": task.id,
            "patient_id": task.patient.id,
            "has_email": bool(task.patient.email),
            "has_user": bool(task.patient.user),
        },
    )

    if task.patient.user:
        # they've already signed up; just send them to their tasks page
        task_url = settings.APP_URL + reverse("patients:patient_details", kwargs={"patient_id": task.patient.id})
        logger.debug(
            "Using direct task URL for existing user", extra={"task_id": task.id, "patient_id": task.patient.id}
        )
        invitation = None
    else:
        # otherwise we need to send them an invitation link
        invitation = find_or_create_patient_invitation(task.patient)
        task_url = settings.APP_URL + reverse("patients:accept_invite", kwargs={"token": invitation.token})
        logger.debug(
            "Using invitation URL for new user",
            extra={"task_id": task.id, "patient_id": task.patient.id, "invitation_id": invitation.id},
        )

    send_templated_email(
        to=task.patient.email,
        subject_template="email/task/send_task_added_subject",
        body_template="email/task/send_task_added_body",
        context={"task": task, "task_url": task_url},
        organization=task.patient.organization,
        language=None,
        email_type=EmailType.task,
        task=task,
        invitation=invitation,
    )

    logger.info("Task notification email sent", extra={"task_id": task.id, "patient_id": task.patient.id})


def assign_default_task_perms(task: Task) -> None:
    # Apply org-wide role perms
    if task.patient.organization:
        for role_name in [RoleName.OWNER, RoleName.ADMIN, RoleName.STAFF]:
            role = task.patient.organization.get_role(role_name)
            assign_perm("view_task", role.group, task)
            assign_perm("change_task", role.group, task)
            assign_perm("complete_task", role.group, task)
        logger.info(
            "Providers from org have been given task permissions",
            extra={
                "organization_id": task.patient.organization.id,
                "patient_id": task.patient.id,
                "task_id": task.id,
            },
        )
    else:
        logger.info(
            "Patient assigned to task does not have org",
            extra={
                "patient_id": task.patient.id,
                "task_id": task.id,
            },
        )
    # Apply patient task perms
    if task.patient.user:
        assign_perm("view_task", task.patient.user, task)
        assign_perm("complete_task", task.patient.user, task)
        logger.info(
            "Patient has been given task permissions",
            extra={
                "patient_id": task.patient.id,
                "task_id": task.id,
            },
        )
    else:
        logger.info(
            "Patient has no associated user for task permissions",
            extra={
                "patient_id": task.patient.id,
                "task_id": task.id,
            },
        )


def ordered_tasks_for_encounter(encounter: Encounter) -> list[Task]:
    """
    Return tasks for an encounter ordered by status and updated_at.
    """
    rank = Case(
        When(status__in=[s.value for s in ACTIVE_TASK_STATUSES], then=Value(0)),
        When(status__in=[s.value for s in TERMINAL_TASK_STATUSES], then=Value(1)),
        default=Value(2),
        output_field=IntegerField(),
    )
    qs = encounter.task_set.annotate(_rank=rank).order_by("_rank", "-updated_at", "-created_at")
    return list(qs)
