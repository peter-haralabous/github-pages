import logging

from django.template import loader

from sandwich.core.models import Patient
from sandwich.core.service.sse_service import EventType
from sandwich.core.service.sse_service import sse_patient_channel
from sandwich.core.service.sse_service import sse_send
from sandwich.core.service.template_service import ContextDict

logger = logging.getLogger(__name__)


def send_assistant_thinking(patient: Patient, message_id: str) -> None:
    sse_send(
        sse_patient_channel(patient),
        EventType.ASSISTANT_THINKING,
        loader.render_to_string(
            "patient/chatty/partials/assistant_message_skeleton.html",
            context={"oob": True, "message_id": "assistant-thinking"},
        ),
    )


def send_assistant_message(patient: Patient, message_id: str, context: ContextDict) -> None:
    sse_send(
        sse_patient_channel(patient),
        EventType.ASSISTANT_MESSAGE,
        loader.render_to_string(
            "patient/chatty/partials/assistant_message.html",
            context={
                "oob": True,
                "message_id": message_id,
                **context,
            },
        ),
    )
