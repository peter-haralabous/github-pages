import logging

from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from sandwich.core.models.invitation import Invitation
from sandwich.core.models.invitation import InvitationStatus
from sandwich.core.models.patient import Patient
from sandwich.core.service.email_service import send_email
from sandwich.users.models import User

logger = logging.getLogger(__name__)

# FIXME-NG: move to settings.py
APP_URL = "http://localhost:3000"


def get_pending_invitation(patient: Patient) -> Invitation | None:
    logger.debug(
        "Checking for pending invitation",
        extra={
            "patient_id": patient.id,
            "organization_id": getattr(patient.organization, "id", "unknown"),
        },
    )

    invitation = patient.invitation_set.filter(status=InvitationStatus.PENDING).first()

    logger.debug(
        "Pending invitation query result",
        extra={
            "patient_id": patient.id,
            "has_pending_invitation": bool(invitation),
            "invitation_id": invitation.id if invitation else None,
        },
    )

    return invitation


def find_or_create_patient_invitation(patient: Patient) -> Invitation:
    """Find an existing pending invitation for the patient, or create a new one."""
    logger.debug(
        "Finding or creating patient invitation",
        extra={
            "patient_id": patient.id,
            "organization_id": getattr(patient.organization, "id", "unknown"),
        },
    )

    invitation = Invitation.objects.filter(patient=patient, status=InvitationStatus.PENDING).first()
    # TODO-NG: reset expires_at when resent

    if not invitation:
        invitation = Invitation.objects.create(patient=patient)
        logger.info(
            "Created new patient invitation",
            extra={
                "patient_id": patient.id,
                "invitation_id": invitation.id,
                "organization_id": getattr(patient.organization, "id", "unknown"),
            },
        )
    else:
        logger.debug(
            "Using existing patient invitation", extra={"patient_id": patient.id, "invitation_id": invitation.id}
        )

    return invitation


def resend_patient_invitation_email(patient: Patient) -> None:
    logger.info(
        "Resending patient invitation email",
        extra={
            "patient_id": patient.id,
            "organization_id": getattr(patient.organization, "id", "unknown"),
            "has_email": bool(patient.email),
        },
    )

    assert patient.organization, "Patient has no organization"

    # this is a bit messy, because we didn't track why the invitation was originally sent
    invitation = find_or_create_patient_invitation(patient)
    task_url = APP_URL + reverse("patients:accept_invite", kwargs={"token": invitation.token})

    to = invitation.patient.email
    subject = "Reminder: you have tasks assigned!"
    body = render_to_string("email/invitation_body.txt", {"invitation": invitation, "task_url": task_url})
    send_email(to, subject, body)

    logger.info("Patient invitation email resent", extra={"patient_id": patient.id, "invitation_id": invitation.id})


def accept_patient_invitation(invitation: Invitation, user: User) -> None:
    logger.info(
        "Accepting patient invitation",
        extra={
            "invitation_id": invitation.id,
            "patient_id": invitation.patient.id,
            "user_id": user.id,
            "organization_id": getattr(invitation.patient.organization, "id", "unknown"),
        },
    )

    assert invitation.status == InvitationStatus.PENDING, "Invitation is not pending"
    assert invitation.patient.user is None, "Patient already has a user"

    invitation.patient.user = user
    invitation.patient.save()

    invitation.status = InvitationStatus.ACCEPTED
    invitation.accepted_at = timezone.now()
    invitation.save()

    logger.info(
        "Patient invitation accepted successfully",
        extra={"invitation_id": invitation.id, "patient_id": invitation.patient.id, "user_id": user.id},
    )
