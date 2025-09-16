from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone

from sandwich.core.models.task import Task
from sandwich.core.models.task import TaskStatus
from sandwich.core.service.invitation_service import find_or_create_patient_invitation

# FIXME-NG: move to settings.py
APP_URL = "http://localhost:3000"


def cancel_task(task: Task) -> None:
    """Cancel a pending task."""
    assert task.active, "Task is not active"
    task.status = TaskStatus.CANCELLED
    task.ended_at = timezone.now()
    task.save()


def complete_task(task: Task) -> None:
    """Complete a task."""
    assert task.active, "Task is not active"
    task.status = TaskStatus.COMPLETED
    task.ended_at = timezone.now()
    task.save()


def send_task_added_email(task: Task) -> None:
    to = task.patient.email
    subject = "You've been assigned a task!"
    if task.patient.user:
        # they've already signed up; just send them to their tasks page
        task_url = APP_URL + reverse("patients:patient_details", kwargs={"patient_id": task.patient.id})
    else:
        # otherwise we need to send them an invite link
        invitation = find_or_create_patient_invitation(task.patient)
        task_url = APP_URL + reverse("patients:accept_invite", kwargs={"token": invitation.token})

    # TODO: generate both html and text versions of the email, add legal footer
    body = f"""Hi {task.patient.first_name},
{task.encounter.organization.name} has assigned you a new task to complete.

Click to get started: {task_url}
    """
    send_mail(subject, body, None, [to])
