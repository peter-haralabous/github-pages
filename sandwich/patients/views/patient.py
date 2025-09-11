from typing import Any

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse

from sandwich.core.models import Patient
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.users.models import User


class PatientEdit(forms.ModelForm[Patient]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit"))

    class Meta:
        model = Patient
        fields = ("first_name", "last_name", "email", "phn", "date_of_birth")
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }


class PatientAdd(forms.ModelForm[Patient]):
    # TODO: add check for duplicate patient
    #       "you already have a patient with this email address/PHN/name"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit"))

    def save(self, commit: bool = True, user: User | None = None) -> Patient:  # noqa: FBT001,FBT002
        instance = super().save(commit=False)
        if user is not None:
            instance.user = user
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Patient
        fields = ("first_name", "last_name", "email", "phn", "date_of_birth")
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }


@login_required
def patient_edit(request: AuthenticatedHttpRequest, patient_id: int) -> HttpResponse:
    patient = get_object_or_404(request.user.patient_set, id=patient_id)
    if request.method == "POST":
        form = PatientEdit(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Patient updated successfully.")
            return HttpResponseRedirect(reverse("patients:patient_details", kwargs={"patient_id": patient_id}))
    else:
        form = PatientEdit(instance=patient)

    context = {"form": form} | _patient_context(request, patient=patient)
    return render(request, "patient/patient_edit.html", context)


@login_required
def patient_add(request: AuthenticatedHttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = PatientAdd(request.POST)
        if form.is_valid():
            patient = form.save(user=request.user)
            messages.add_message(request, messages.SUCCESS, "Patient added successfully.")
            return HttpResponseRedirect(reverse("patients:patient_details", kwargs={"patient_id": patient.id}))
    else:
        form = PatientAdd()

    context = {"form": form} | _patient_context(request)
    return render(request, "patient/patient_add.html", context)


@login_required
def patient_details(request: AuthenticatedHttpRequest, patient_id: int) -> HttpResponse:
    patient = get_object_or_404(request.user.patient_set, id=patient_id)
    tasks = patient.task_set.all()

    context = {"patient": patient, "tasks": tasks} | _patient_context(request, patient=patient)
    return render(request, "patient/patient_details.html", context)


def _patient_context(request: AuthenticatedHttpRequest, patient: Patient | None = None) -> dict[str, Any]:
    """Fetch additional template context required for patient context"""
    return {"patient": patient, "patients": request.user.patient_set.all()}
