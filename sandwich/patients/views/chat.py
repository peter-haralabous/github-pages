import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from sandwich.core.models import Patient
from sandwich.core.service.agent_service.memory import purge_thread
from sandwich.core.service.chat_service.chat import ChatContext
from sandwich.core.service.chat_service.event import UserMessageEvent
from sandwich.core.service.chat_service.event import receive_chat_event
from sandwich.core.service.chat_service.sse import send_user_message
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.patients.forms.chat import ChatForm


@login_required
@require_POST
def chat(request: AuthenticatedHttpRequest) -> HttpResponse:
    form = ChatForm(request.POST, user=request.user)
    if form.is_valid():
        patient = form.cleaned_data["patient"]
        event = UserMessageEvent(context=ChatContext(patient_id=str(patient.id)), content=form.cleaned_data["message"])

        # Update chat history to include the user's message
        send_user_message(event)

        # TODO: move this into an async job
        receive_chat_event(event)

        return HttpResponse()
    logging.error("Invalid chat form: %s", form.errors)

    context = {"chat_form": form}
    return render(request, "patient/chatty/partials/chat_form.html", context)


@login_required
@require_POST
@authorize_objects([ObjPerm(Patient, "patient_id", ["change_patient"])])
def clear_chat(request: AuthenticatedHttpRequest, patient: Patient) -> HttpResponse:
    # Create context to get the thread_id
    context = ChatContext(patient_id=str(patient.id))

    # Purge the thread
    purge_thread(context.thread_id)
    logging.warning("Chat cleared for patient", extra={"patient_id": patient.id})

    # Return HX-Refresh header to reload the page
    response = HttpResponse()
    response["HX-Refresh"] = "true"
    return response
