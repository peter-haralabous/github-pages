import logging
from enum import StrEnum

from django_eventstream import send_event

from sandwich.core.models import Patient
from sandwich.core.types import JsonValue

logger = logging.getLogger(__name__)


class EventType(StrEnum):
    ASSISTANT_MESSAGE = "assistant_message"
    ASSISTANT_THINKING = "assistant_thinking"
    FEED_ITEM = "feed_item"
    RECORDS_UPDATED = "records_updated"
    USER_MESSAGE = "user_message"


def sse_patient_channel(patient: Patient) -> str:
    return f"patient/{patient.id}"


def sse_send_html(channel: str, event_type: EventType, content: str) -> None:
    logger.debug("Sending SSE html", extra={"event_type": event_type.value, "channel": channel})
    send_event(channel, event_type.value, content, json_encode=False)


def sse_send_json(channel: str, event_type: EventType, content: JsonValue) -> None:
    logger.debug("Sending SSE json", extra={"event_type": event_type.value, "channel": channel})
    send_event(channel, event_type.value, content, json_encode=True)
