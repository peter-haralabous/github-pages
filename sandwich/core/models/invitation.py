from datetime import datetime
from datetime import timedelta
from secrets import token_urlsafe

from django.db import models
from django.utils import timezone
from django_enum import EnumField

from sandwich.core.models.abstract import BaseModel


class InvitationStatus(models.TextChoices):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    FAILED_VERIFICATION = "FAILED_VERIFICATION"
    FAILED = "FAILED"


INVITE_EXPIRY_DAYS = 90


def default_expiry() -> datetime:
    return timezone.now() + timedelta(days=INVITE_EXPIRY_DAYS)


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
