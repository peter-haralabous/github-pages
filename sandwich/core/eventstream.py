import logging

from django.http import HttpRequest
from django_eventstream.channelmanager import DefaultChannelManager
from django_eventstream.views import events

from sandwich.core.models import Patient
from sandwich.users.models import User

logger = logging.getLogger(__name__)


class ChannelManager(DefaultChannelManager):
    def can_read_channel(self, user: User | None, channel: str):
        logger.debug("Checking channel permissions", extra={"channel": channel})
        if not user or user.is_anonymous:
            return False
        try:
            # TODO: define what channels exist and who can read them
            if channel.startswith("patient/"):
                patient_id = channel.removeprefix("patient/")
                patient = Patient.objects.get(id=patient_id)
                return user.has_perm("view_patient", patient)
        except Exception:  # noqa: BLE001
            logger.warning("Error while checking channel permissions", extra={"channel": channel}, exc_info=True)
        return False


def events_view(request: HttpRequest, **kwargs):
    response = events(request, **kwargs)
    # without no-transform webpack-dev-server will buffer the stream
    # https://github.com/chimurai/http-proxy-middleware/issues/371
    response.headers["Cache-Control"] = "no-cache, no-transform"
    return response
