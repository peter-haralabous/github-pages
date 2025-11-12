import logging

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html

from sandwich.core.models import Fact
from sandwich.core.models import Patient
from sandwich.core.service.health_record_service import get_total_health_record_count
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.core.validators.date_time import not_in_future
from sandwich.patients.views.patient import _chat_context

logger = logging.getLogger(__name__)


def _chatty_patient_details_context(request: AuthenticatedHttpRequest, patient: Patient):
    records_count = get_total_health_record_count(patient)
    repository_count = patient.document_set.count()
    return {
        "records_count": records_count,
        "repository_count": repository_count,
    } | _chat_context(request, patient=patient)


@login_required
@authorize_objects([ObjPerm(Patient, "patient_id", ["view_patient"])])
def patient_details(request: AuthenticatedHttpRequest, patient: Patient) -> HttpResponse:
    template = "patient/chatty/app.html"
    context = _chatty_patient_details_context(request, patient)

    if request.headers.get("HX-Target") == "left-panel":
        template = "patient/chatty/partials/left_panel.html"

    return render(request, template, context)


class FactEditModalForm(forms.ModelForm[Fact]):
    start_datetime = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        label="Start Date/Time",
        validators=[not_in_future],
    )
    end_datetime = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        label="End Date/Time",
        validators=[not_in_future],
    )

    class Meta:
        model = Fact
        fields = ["start_datetime", "end_datetime"]

    def __init__(self, *args, **kwargs) -> None:
        form_action = kwargs.pop("form_action", "")
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(
            Submit(
                "submit",
                "Save",
                hx_post=reverse("patients:fact_edit", args=(self.instance.id,)),
                hx_target="#form-modal",
            )
        )

        if form_action:
            self.helper.form_action = form_action

    def clean(self):
        start_datetime = self.cleaned_data.get("start_datetime")
        end_datetime = self.cleaned_data.get("end_datetime")
        if start_datetime and end_datetime and end_datetime < start_datetime:
            raise forms.ValidationError("End date/time cannot be earlier than start date/time.")
        return self.cleaned_data


@login_required
@authorize_objects([ObjPerm(Fact, "fact_id", ["change_fact"])])
def fact_edit(request: AuthenticatedHttpRequest, fact: Fact) -> HttpResponse:
    """View to power the fact edit modal"""

    if request.method == "POST":
        form = FactEditModalForm(request.POST, instance=fact, form_action=request.path)
        if form.is_valid():
            form.save()

            # Return the now empty modal to close it and refresh the fact card using hx-swap-oob
            # Note the use of <template> because > https://htmx.org/attributes/hx-swap-oob/#troublesome-tables-and-lists
            return HttpResponse(
                format_html(
                    "{modal}<template>{row}</template>",
                    modal="",
                    row=render_to_string("patient/partials/card_fact.html", {"fact": fact, "oob": True}),
                )
            )
    else:
        form = FactEditModalForm(instance=fact, form_action=request.path)

    context = {"fact": fact, "form": form}
    return render(request, "patient/partials/fact_edit_modal.html", context)
