from typing import Any

from sandwich.core.models.patient import Patient
from sandwich.core.service.agent_service.config import configure
from sandwich.core.service.chat_service.chat import load_chat_messages
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.patients.views.chat import ChatForm


def _patient_context(request: AuthenticatedHttpRequest, patient: Patient | None = None) -> dict[str, Any]:
    """Fetch additional template context required for patient context"""
    return {
        # used to show the right name in the top nav
        # and contextualizes all the links in the side nav
        "patient": patient
    }


def _chat_context(request: AuthenticatedHttpRequest, patient: Patient) -> dict[str, Any]:
    """Fetch additional template context required for chat context"""
    # this hard-coded chat thread will need to be updated when we support multiple threads
    chat_thread = f"{request.user.pk}-{patient.pk}"
    return _patient_context(request, patient=patient) | {
        "chat_form": ChatForm(user=request.user, initial={"patient": patient, "thread": chat_thread}),
        "chat_messages": load_chat_messages(configure(chat_thread), patient),
    }
