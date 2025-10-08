import json
import logging

from anymail.signals import post_send
from anymail.signals import tracking
from django.conf import settings
from django.core.mail import EmailMessage
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

    msg = EmailMessage(
        subject=subject,
        body=body,
        from_email=None,
        to=[to],
    )
    msg.content_subtype = "html"
    email = Email.objects.create(to=to, type=email_type, invitation=invitation, task=task)
    # Note: the email id header allows the post send signal to find the correct
    # email record to update. This is done in favour of using msg.anymail.message_id
    # to avoid switching EmailMessage to AnymailMessage.
    # https://anymail.dev/en/stable/sending/anymail_additions/#anymail.message.AnymailStatus
    msg.extra_headers["X-Email-Id"] = f'{{"email_id": "{email.id}"}}'

    try:
        msg.send()
        logger.info("Email sent successfully", extra={"has_recipient": bool(to)})
    except Exception as e:
        # TODO: failed to send. update email record
        logger.exception("Failed to send email", extra={"error_type": type(e).__name__})


@receiver(post_send)
def email_sent_post_process(sender, message, status, esp_name, **kwargs):
    logger.info("Email post send processing started")
    for recipient_status in status.recipients.items():
        email_id_header = message.extra_headers.get("X-Email-Id")
        if email_id_header:
            header_dict = json.loads(email_id_header)
            try:
                email = Email.objects.get(id=header_dict.get("email_id"))
                email.status = recipient_status.status
                email.message_id = recipient_status.message_id  # might be None if send failed
                logger.info(
                    "Updating email record",
                    extra={
                        "email_id": email.id,
                        "message_id": recipient_status.message_id,
                        "status": recipient_status.status,
                    },
                )
                email.save(update_fields=["status", "message_id"])
            except Exception as e:
                logger.exception(
                    "Failed to update status and message_id on email",
                    extra={"message_id": recipient_status.message_id, "error_type": type(e).__name__},
                )
    logger.info("Email post send processing finished")


@receiver(tracking)
def handle_tracking(sender, event, esp_name, **kwargs):
    if esp_name == "Amazon SES":
        logger.info("Received email tracking event")
        if event.event_type == "bounced":
            logger.warning("Email bounced", extra={"reason": event.reject_reason, "message_id": event.message_id})
            email = Email.objects.get(message_id=event.message_id)
            email.status = EmailStatus.BOUNCED
            email.save(update_fields=["status"])
            invitation = Invitation.objects.get(id=email.invitation.id) if email.invitation else None

            if invitation:
                invitation.status = InvitationStatus.FAILED
                invitation.save(update_fields=["status"])
