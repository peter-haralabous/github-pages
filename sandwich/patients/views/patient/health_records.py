import logging
from uuid import UUID

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse

from sandwich.core.models import Immunization
from sandwich.core.models import Patient
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.core.validators.date_time import not_in_future
from sandwich.patients.views.patient import _patient_context

logger = logging.getLogger(__name__)


@login_required
@authorize_objects([ObjPerm(Patient, "patient_id", ["view_patient"])])
def health_records(request: AuthenticatedHttpRequest, patient: Patient):
    documents = patient.document_set.all()
    immunizations = patient.immunization_set.all()

    context = {
        "patient": patient,
        "documents": documents,
        "immunizations": immunizations,
    } | _patient_context(request, patient=patient)
    return render(request, "patient/health_records.html", context)


class ImmunizationForm(forms.ModelForm[Immunization]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].validators.append(not_in_future)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit"))

    class Meta:
        model = Immunization
        fields = ("name", "date")

    def save(self, *, patient: Patient, commit: bool = True) -> Immunization:  # type: ignore[override]
        instance = super().save(commit=False)
        instance.patient = patient
        if commit:
            instance.save()
        return instance


def _form_class(record_type: str):
    if record_type == "immunization":
        return ImmunizationForm
    raise ValueError(f"Unknown form class: {record_type}")


@login_required
@authorize_objects([ObjPerm(Patient, "patient_id", ["view_patient", "change_patient"])])
def health_records_add(request: AuthenticatedHttpRequest, patient: Patient, record_type: str):
    form_class = _form_class(record_type)
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            form.save(patient=patient)
            return HttpResponseRedirect(reverse("patients:health_records", kwargs={"patient_id": patient.id}))
    else:
        form = form_class()

    context = {
        "record_type": record_type,
        "record_type_name": form_class.Meta.model._meta.verbose_name,  # noqa: SLF001
        "form": form,
    } | _patient_context(request, patient=patient)
    return render(request, "patient/health_records_add.html", context)


def _generic_edit_view(record_type: str, request: AuthenticatedHttpRequest, patient: Patient, instance):
    form_class = _form_class(record_type)
    if request.method == "DELETE":
        instance.delete()
        if request.headers.get("HX-Request") == "true":
            # FIXME: doing row-by-row deletes means removing the last row doesn't re-add the empty state
            #        consider re-rendering the entire table instead, like how document_delete does it
            return HttpResponse(status=200)
        return HttpResponseRedirect(reverse("patients:health_records", kwargs={"patient_id": patient.id}))
    if request.method == "POST":
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save(patient=patient)
            return HttpResponseRedirect(reverse("patients:health_records", kwargs={"patient_id": patient.id}))
    else:
        form = form_class(instance=instance)
    context = {
        "record_type": record_type,
        "record_type_name": form_class.Meta.model._meta.verbose_name,  # noqa: SLF001
        "form": form,
    } | _patient_context(request, patient=patient)
    return render(request, "patient/health_records_edit.html", context)


@login_required
def immunization_edit(request: AuthenticatedHttpRequest, immunization_id: UUID):
    model = Immunization
    instance = get_object_or_404(model, id=immunization_id)
    if not request.user.has_perms(["view_patient", "change_patient"], instance.patient):
        raise Http404(f"No {model._meta.object_name} matches the given query.")  # noqa: SLF001
    return _generic_edit_view("immunization", request, instance.patient, instance)
