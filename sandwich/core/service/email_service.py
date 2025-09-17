import logging

from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_email(to, subject, body):
    # TODO: set up bounce tracking, etc.
    # see https://anymail.dev/en/stable/esps/amazon_ses/#status-tracking-webhooks
    if not to:
        # TODO: should this throw instead?
        logger.warning("dropping email because no recipient was specified")
    send_mail(subject, body, None, [to])
