import logging
from typing import TYPE_CHECKING

from crispy_forms.helper import FormHelper
from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from guardian.shortcuts import get_objects_for_user

from sandwich.core.inputs import RoundIconButton
from sandwich.core.models import Patient
from sandwich.core.service.agent_service.config import configure
from sandwich.core.service.chat_service.chat import receive_chat_message
from sandwich.core.service.markdown_service import markdown_to_html
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.users.models import User

if TYPE_CHECKING:
    from sandwich.core.service.chat_service.response import ChatResponse


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
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.add_input(
            RoundIconButton(
                icon="arrow-up",
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
        user = request.user
        patient = form.cleaned_data["patient"]
        thread = f"{user.pk}-{patient.pk}"  # Hard code for now
        message = form.cleaned_data["message"]
        response: ChatResponse = receive_chat_message(
            user=user,
            patient=patient,
            config=configure(thread),
            message=message,
        )
        context = {"message": markdown_to_html(response.message), "buttons": response.buttons}
        return render(request, "patient/chatty/partials/assistant_message.html", context)
    logging.error("Invalid chat form: %s", form.errors)
    context = {"message": str(form.errors) if settings.DEBUG else "An error has occurred"}
    return render(request, "patient/chatty/partials/assistant_message.html", context)
