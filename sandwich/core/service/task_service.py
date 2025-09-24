import logging

from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from sandwich.core.models.task import Task
from sandwich.core.models.task import TaskStatus
from sandwich.core.service.email_service import send_email
from sandwich.core.service.invitation_service import find_or_create_patient_invitation

logger = logging.getLogger(__name__)

# FIXME-NG: move to settings.py
APP_URL = "http://localhost:3000"


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

    to = task.patient.email
    subject = "You've been assigned a task!"

    if task.patient.user:
        # they've already signed up; just send them to their tasks page
        task_url = APP_URL + reverse("patients:patient_details", kwargs={"patient_id": task.patient.id})
        logger.debug(
            "Using direct task URL for existing user", extra={"task_id": task.id, "patient_id": task.patient.id}
        )
    else:
        # otherwise we need to send them an invitation link
        invitation = find_or_create_patient_invitation(task.patient)
        task_url = APP_URL + reverse("patients:accept_invite", kwargs={"token": invitation.token})
        logger.debug(
            "Using invitation URL for new user",
            extra={"task_id": task.id, "patient_id": task.patient.id, "invitation_id": invitation.id},
        )

    body = render_to_string("email/task_added_body.txt", {"task": task, "task_url": task_url})
    send_email(to, subject, body)

    logger.info("Task notification email sent", extra={"task_id": task.id, "patient_id": task.patient.id})
