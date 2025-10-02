import logging

from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


def send_email(to, subject, body):
    logger.info(
        "Sending email",
        extra={
            "has_recipient": bool(to),
            "subject_length": len(subject) if subject else 0,
            "body_length": len(body) if body else 0,
        },
    )

    # TODO: set up bounce tracking, etc.
    # see https://anymail.dev/en/stable/esps/amazon_ses/#status-tracking-webhooks
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

    try:
        msg.send()
        logger.info("Email sent successfully", extra={"has_recipient": bool(to)})
    except Exception as e:
        logger.exception("Failed to send email", extra={"error_type": type(e).__name__})
