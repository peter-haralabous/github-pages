import logging

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from guardian.shortcuts import assign_perm
from procrastinate.contrib.django import app

from sandwich.core.models.email import EmailType
from sandwich.core.models.invitation import Invitation
from sandwich.core.models.invitation import InvitationStatus
from sandwich.core.models.patient import Patient
from sandwich.core.models.role import RoleName
from sandwich.core.service.email_service import send_templated_email
from sandwich.core.service.organization_service import assign_organization_role
from sandwich.users.models import User

logger = logging.getLogger(__name__)


def get_unaccepted_invitation(patient: Patient) -> Invitation | None:
    logger.debug(
        "Checking for pending invitation",
        extra={
            "patient_id": patient.id,
            "organization_id": getattr(patient.organization, "id", "unknown"),
        },
    )

    invitation = patient.invitation_set.exclude(status=InvitationStatus.ACCEPTED).first()

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
    task_url = settings.APP_URL + reverse("patients:accept_invite", kwargs={"token": invitation.token})

    send_templated_email(
        to=invitation.patient.email,
        subject_template="email/invitation/resend_patient_invitation_subject",
        body_template="email/invitation/resend_patient_invitation_body",
        context={"invitation": invitation, "task_url": task_url},
        organization=patient.organization,
        language=None,
        email_type=EmailType.invitation,
        invitation=invitation,
    )

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

    patient = invitation.patient
    patient.user = user
    patient.save()
    patient.assign_user_owner_perms(user)

    if patient.organization:
        assign_organization_role(patient.organization, RoleName.PATIENT, patient.user)

    invitation.status = InvitationStatus.ACCEPTED
    invitation.accepted_at = timezone.now()
    invitation.save()

    logger.info(
        "Patient invitation accepted successfully",
        extra={"invitation_id": invitation.id, "patient_id": invitation.patient.id, "user_id": user.id},
    )


def expire_invitations() -> int:
    """
    Update Invitations.status to EXPIRED if the current datetime is past the Invitation.expires_at datetime
    """
    logger.debug("Updating invitation status to EXPIRED for invitations past their expires_at datetime")
    expired_count = (
        Invitation.objects.exclude(expires_at=None)
        .filter(expires_at__lt=timezone.now())
        .filter(status=InvitationStatus.PENDING)
        .update(status=InvitationStatus.EXPIRED)
    )
    logger.info("Expired %d invitations", expired_count)
    return expired_count


@app.periodic(cron="0 * * * *")  # every hour
@app.task(lock="expire_invitations_lock")
def expire_invitations_job(timestamp: int) -> None:
    expire_invitations()


DEFAULT_ORGANIZATION_ROLE_PERMS = {
    RoleName.OWNER: ["change_invitation", "view_invitation"],
    RoleName.ADMIN: ["change_invitation", "view_invitation"],
    RoleName.STAFF: ["change_invitation", "view_invitation"],
}


def assign_default_invitation_perms(invitation: Invitation) -> None:
    """
    Assign permissisions to an invitation.
    A patient should have view and change permissions on the invitation.

    roles in the invited patient's org should have permissions to view and change the invitation.
    """
    if invitation.patient.user:
        assign_perm("view_invitation", invitation.patient.user, invitation)
        assign_perm("change_invitation", invitation.patient.user, invitation)

    # An invited patient _should_ be a part of the org
    # but just in case they're not let's add this guard.
    organization = invitation.patient.organization
    if organization:
        for role_name, perms in DEFAULT_ORGANIZATION_ROLE_PERMS.items():
            role = organization.get_role(role_name)
            for perm in perms:
                assign_perm(perm, role.group, invitation)
