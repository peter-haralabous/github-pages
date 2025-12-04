from anymail.signals import EventType
from django.db import models

from sandwich.core.models.abstract import BaseModel


class EmailType(models.TextChoices):
    invitation = "invitation", "Invitation"
    task = "task", "Task"


class EmailStatus(models.TextChoices):
    """
    This set of values comes from the signal types supported by anymail.
    https://anymail.dev/en/stable/sending/tracking/#anymail.signals.AnymailTrackingEvent.event_type

    We do not use all of them. Our current setup uses SNS Notifcations
    which only support Bounced, Delivered, Complained statuses.
    https://docs.aws.amazon.com/ses/latest/dg/notification-examples.html
    https://anymail.dev/en/stable/esps/amazon_ses/#status-tracking-webhooks
    """

    AUTORESPONDED = EventType.AUTORESPONDED, "Autoresponded"
    BOUNCED = EventType.BOUNCED, "Bounced"
    CLICKED = EventType.CLICKED, "Clicked"
    COMPLAINED = EventType.COMPLAINED, "Complained"
    DEFERRED = EventType.DEFERRED, "Deferred"
    DELIVERED = EventType.DELIVERED, "Delivered"
    FAILED = EventType.FAILED, "Failed"
    INBOUND = EventType.INBOUND, "Inbound"
    INBOUND_FAILED = EventType.INBOUND_FAILED, "Inbound Failed"
    OPENED = EventType.OPENED, "Opened"
    QUEUED = EventType.QUEUED, "Queued"
    REJECTED = EventType.REJECTED, "Rejected"
    SENT = EventType.SENT, "Sent"
    SUBSCRIBED = EventType.SUBSCRIBED, "Subscribed"
    UNKNOWN = EventType.UNKNOWN, "Unknown"
    UNSUBSCRIBED = EventType.UNSUBSCRIBED, "Unsubscribed"


class Email(BaseModel):
    to = models.EmailField()
    type = models.TextField(choices=EmailType)
    status = models.CharField(max_length=50, choices=EmailStatus, blank=True, default="")
    message_id = models.TextField(blank=True, default="")  # from ses
    invitation = models.ForeignKey("Invitation", on_delete=models.CASCADE, null=True)
    task = models.ForeignKey("Task", on_delete=models.CASCADE, null=True)
