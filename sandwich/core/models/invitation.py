from datetime import datetime
from datetime import timedelta
from secrets import token_urlsafe

from django.db import models
from django.utils import timezone
from django_enum import EnumField

from sandwich.core.models.abstract import BaseModel
from sandwich.core.models.organization import VerificationType


class InvitationStatus(models.TextChoices):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    FAILED_VERIFICATION = "FAILED_VERIFICATION"
    FAILED = "FAILED"


INVITE_EXPIRY_DAYS = 90
MAX_VERIFICATION_ATTEMPTS = 3


def default_expiry() -> datetime:
    return timezone.now() + timedelta(days=INVITE_EXPIRY_DAYS)


class InvitationManager(models.Manager["Invitation"]):
    def create(self, **kwargs) -> "Invitation":
        from sandwich.core.service.invitation_service import assign_default_invitation_perms  # noqa: PLC0415

        created = super().create(**kwargs)
        assign_default_invitation_perms(created)
        return created


class Invitation(BaseModel):
    status: models.Field[InvitationStatus, InvitationStatus] = EnumField(
        InvitationStatus,
        default=InvitationStatus.PENDING,
    )
    # The token isn't visible to the sender, only to the receiver
    token = models.CharField(default=token_urlsafe, editable=False, unique=True)

    expires_at = models.DateTimeField(default=default_expiry, null=True)
    accepted_at = models.DateTimeField(null=True)
    last_invited_at = models.DateTimeField(default=timezone.now)

    patient = models.ForeignKey("Patient", on_delete=models.CASCADE)
    verification_attempts = models.PositiveIntegerField(default=0, help_text="number of failed verification attempts")

    objects = InvitationManager()

    @property
    def verification_type(self) -> VerificationType:
        organization = self.patient.organization if self.patient else None
        return organization.verification_type if organization else VerificationType.NONE

    def increment_verification_attempts(self) -> None:
        """Increment verification attempts and update status if limit exceeded."""
        self.verification_attempts += 1
        if self.verification_attempts >= MAX_VERIFICATION_ATTEMPTS:
            self.status = InvitationStatus.FAILED_VERIFICATION
        self.save(update_fields=["verification_attempts", "status"])

    def get_remaining_verification_attempts(self) -> int:
        return MAX_VERIFICATION_ATTEMPTS - self.verification_attempts
