import logging

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML
from django import forms
from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST
from guardian.shortcuts import get_objects_for_user

from sandwich.core.models import Patient
from sandwich.core.service.chat_service.chat import ChatContext
from sandwich.core.service.chat_service.chat import UserMessageEvent
from sandwich.core.service.chat_service.chat import receive_chat_event
from sandwich.core.service.chat_service.sse import send_user_message
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.users.models import User


class ChatForm(forms.Form):
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.none(),  # Queryset populated in __init__
        required=True,
        widget=forms.HiddenInput,
    )
    message = forms.CharField(
        required=True, widget=forms.Textarea(attrs={"placeholder": "Ask a question or add notes..."})
    )
    thread = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, user: User, **kwargs):
        self._user = user
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.form_action = reverse("patients:chat")
        self.helper.attrs = {
            "hx-post": reverse("patients:chat"),
            "hx-disabled-elt": "find button, find textarea",
            "hx-swap": "none",
        }
        self.helper.form_show_labels = False
        assert self.helper.layout is not None, "layout should not be None"
        self.helper.layout.append(
            HTML(
                '{% load lucide %}<button type="submit" class="btn btn-primary btn-circle absolute bottom-2.5 right-2.5 z-100">{% lucide "arrow-up" %}</button>'  # noqa: E501
            )
        )
        self.fields["patient"].queryset = self._patient_queryset()  # type: ignore[attr-defined]

    def _patient_queryset(self) -> QuerySet[Patient]:
        return get_objects_for_user(self._user, "view_patient", Patient)


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
