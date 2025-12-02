from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML
from django import forms
from django.db.models import QuerySet
from django.urls import reverse
from guardian.shortcuts import get_objects_for_user

from sandwich.core.models import Patient
from sandwich.users.models import User


class ChatForm(forms.Form):
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.none(),  # Queryset populated in __init__
        required=True,
        widget=forms.HiddenInput,
    )
    message = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={
                "placeholder": "Ask a question or add notes...",
                # Use soft wrap and CSS to force wrapping across browsers and with Tailwind
                "wrap": "soft",
                "class": "whitespace-pre-wrap break-words wrap-anywhere",
            }
        ),
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
