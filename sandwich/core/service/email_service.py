import logging

from anymail.message import AnymailMessage
from anymail.signals import EventType
from anymail.signals import tracking
from django.conf import settings
from django.dispatch import receiver

from sandwich.core.models import Email
from sandwich.core.models import Invitation
from sandwich.core.models import Organization
from sandwich.core.models import Task
from sandwich.core.models.email import EmailStatus
from sandwich.core.models.email import EmailType
from sandwich.core.models.invitation import InvitationStatus
from sandwich.core.service.template_service import render
from sandwich.core.types import HtmlStr

logger = logging.getLogger(__name__)
ANYMAIL_INSTALLED = "anymail" in settings.INSTALLED_APPS


def send_templated_email(  # noqa: PLR0913
    to: str,
    subject_template: str,
    body_template: str,
    context: dict[str, object],
    email_type=EmailType.task,
    organization: Organization | None = None,
    language: str | None = None,
    invitation: Invitation | None = None,
    task: Task | None = None,
):
    context.setdefault("app_url", settings.APP_URL)
    subject = render(
        template_name=subject_template,
        organization=organization,
        language=language,
        context=context,
        as_markdown=False,
    )
    body = render(template_name=body_template, organization=organization, language=language, context=context)
    send_email(to, subject, body, email_type=email_type, invitation=invitation, task=task)


def send_email(  # noqa: PLR0913
    to: str,
    subject: str,
    body: HtmlStr,
    email_type: EmailType,
    invitation: Invitation | None = None,
    task: Task | None = None,
):
    logger.info(
        "Sending email",
        extra={
            "has_recipient": bool(to),
            "subject_length": len(subject) if subject else 0,
            "body_length": len(body) if body else 0,
        },
    )

    if not to:
        # TODO: should this throw instead?
        logger.warning("Dropping email - no recipient specified", extra={"subject": subject})
        return

    msg = AnymailMessage(
        subject=subject,
        body=body,
        from_email=None,
        to=[to],
    )
    msg.content_subtype = "html"

    try:
        sent = msg.send()
        if sent > 0:  # This should only ever be 1 (an email was sent) or 0 (something went wrong)
            record_email_delivery(to, email_type, msg, invitation, task)
        logger.info("Email sent successfully", extra={"has_recipient": bool(to)})
    except Exception as e:
        logger.exception("Failed to send email", extra={"error_type": type(e).__name__})


def record_email_delivery(
    to: str, email_type: EmailType, msg: AnymailMessage, invitation: Invitation | None = None, task: Task | None = None
):
    if ANYMAIL_INSTALLED:
        recipient = next(iter(msg.anymail_status.recipients.values()))
        status = recipient.status
        message_id = recipient.message_id
    else:
        status = EmailStatus.SENT
        message_id = ""
    Email.objects.create(
        to=to, type=email_type, message_id=message_id, status=status, invitation=invitation, task=task
    )


# Note: We don't expect handle_tracking to fire locally as
# emails locally do not go though SES or anymail
@receiver(tracking)
def handle_tracking(sender, event, esp_name, **kwargs):
    logger.info("Received email tracking event")
    if esp_name == "Amazon SES":
        if event.event_type == EventType.BOUNCED:
            logger.warning("Email bounced", extra={"reason": event.reject_reason, "message_id": event.message_id})
            email = Email.objects.get(message_id=event.message_id)
            email.status = EmailStatus.BOUNCED
            email.save(update_fields=["status"])
            invitation = Invitation.objects.get(id=email.invitation.id) if email.invitation else None

            if invitation:
                invitation.status = InvitationStatus.FAILED
                invitation.save(update_fields=["status"])
        elif event.event_type == EventType.DELIVERED:
            email = Email.objects.get(message_id=event.message_id)
            email.status = EmailStatus.DELIVERED
            email.save(update_fields=["status"])
        elif event.event_type == EventType.COMPLAINED:
            email = Email.objects.get(message_id=event.message_id)
            email.status = EmailStatus.COMPLAINED
            email.save(update_fields=["status"])
        else:
            logger.info("Unhandled tracking event", extra={"event": event.event_type})
    logger.info("Finished processing email tracking event")
