from django.urls import reverse
from django.utils import timezone

from sandwich.core.models.invitation import Invitation
from sandwich.core.models.invitation import InvitationStatus
from sandwich.core.models.patient import Patient
from sandwich.core.service.email_service import send_email
from sandwich.users.models import User

# FIXME-NG: move to settings.py
APP_URL = "http://localhost:3000"


def get_pending_invitation(patient: Patient) -> Invitation | None:
    return patient.invitation_set.filter(status=InvitationStatus.PENDING).first()


def find_or_create_patient_invitation(patient: Patient) -> Invitation:
    """Find an existing pending invitation for the patient, or create a new one."""
    invitation = Invitation.objects.filter(patient=patient, status=InvitationStatus.PENDING).first()
    # TODO-NG: reset expires_at when resent

    if not invitation:
        invitation = Invitation.objects.create(patient=patient)
    return invitation


def resend_patient_invitation_email(patient: Patient) -> None:
    assert patient.organization, "Patient has no organization"

    # this is a bit messy, because we didn't track why the invitation was originally sent
    invitation = find_or_create_patient_invitation(patient)

    to = invitation.patient.email
    subject = "Reminder: you have tasks assigned!"
    task_url = APP_URL + reverse("patients:accept_invite", kwargs={"token": invitation.token})
    body = f"""Hi {invitation.patient.first_name},
{patient.organization.name} has assigned you a tasks to complete.

Click to get started: {task_url}
"""
    send_email(to, subject, body)


def accept_patient_invitation(invitation: Invitation, user: User) -> None:
    assert invitation.status == InvitationStatus.PENDING, "Invitation is not pending"
    assert invitation.patient.user is None, "Patient already has a user"

    invitation.patient.user = user
    invitation.patient.save()

    invitation.status = InvitationStatus.ACCEPTED
    invitation.accepted_at = timezone.now()
    invitation.save()
