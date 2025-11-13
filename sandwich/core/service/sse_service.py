import logging
from enum import StrEnum

from django_eventstream import send_event

from sandwich.core.models import Patient
from sandwich.core.types import JsonArray
from sandwich.core.types import JsonObject

logger = logging.getLogger(__name__)


class EventType(StrEnum):
    ASSISTANT_MESSAGE = "assistant_message"
    ASSISTANT_THINKING = "assistant_thinking"
    INGEST_PROGRESS = "ingest_progress"


def sse_patient_channel(patient: Patient) -> str:
    return f"patient/{patient.id}"


def sse_send(channel: str, event_type: EventType, content: str | JsonArray | JsonObject) -> None:
    logger.debug("Sending SSE event", extra={"event_type": event_type.value, "channel": channel, "content": content})
    send_event(channel, event_type.value, content, json_encode=not isinstance(content, str))
