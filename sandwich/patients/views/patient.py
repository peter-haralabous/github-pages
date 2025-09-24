import logging
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

from sandwich.core.models.patient import Patient
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.users.models import User

logger = logging.getLogger(__name__)


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
    logger.info("Accessing patient edit", extra={"user_id": request.user.id, "patient_id": patient_id})

    patient = get_object_or_404(request.user.patient_set, id=patient_id)
    if request.method == "POST":
        logger.info("Processing patient edit form", extra={"user_id": request.user.id, "patient_id": patient_id})
        form = PatientEdit(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            logger.info("Patient updated successfully", extra={"user_id": request.user.id, "patient_id": patient_id})
            messages.add_message(request, messages.SUCCESS, "Patient updated successfully.")
            return HttpResponseRedirect(reverse("patients:patient_details", kwargs={"patient_id": patient_id}))
        logger.warning(
            "Invalid patient edit form",
            extra={"user_id": request.user.id, "patient_id": patient_id, "form_errors": list(form.errors.keys())},
        )
    else:
        logger.debug("Rendering patient edit form", extra={"user_id": request.user.id, "patient_id": patient_id})
        form = PatientEdit(instance=patient)

    context = {"form": form} | _patient_context(request, patient=patient)
    return render(request, "patient/patient_edit.html", context)


@login_required
def patient_add(request: AuthenticatedHttpRequest) -> HttpResponse:
    logger.info("Accessing patient add", extra={"user_id": request.user.id})

    if request.method == "POST":
        logger.info("Processing patient add form", extra={"user_id": request.user.id})
        form = PatientAdd(request.POST)
        if form.is_valid():
            patient = form.save(user=request.user)
            logger.info("Patient created successfully", extra={"user_id": request.user.id, "patient_id": patient.id})
            messages.add_message(request, messages.SUCCESS, "Patient added successfully.")
            return HttpResponseRedirect(reverse("patients:patient_details", kwargs={"patient_id": patient.id}))
        logger.warning(
            "Invalid patient add form", extra={"user_id": request.user.id, "form_errors": list(form.errors.keys())}
        )
    else:
        logger.debug("Rendering patient add form", extra={"user_id": request.user.id})
        form = PatientAdd()

    context = {"form": form} | _patient_context(request)
    return render(request, "patient/patient_add.html", context)


@login_required
def patient_details(request: AuthenticatedHttpRequest, patient_id: int) -> HttpResponse:
    logger.info("Accessing patient details", extra={"user_id": request.user.id, "patient_id": patient_id})

    patient = get_object_or_404(request.user.patient_set, id=patient_id)
    tasks = patient.task_set.all()

    logger.debug(
        "Patient details loaded",
        extra={"user_id": request.user.id, "patient_id": patient_id, "task_count": tasks.count()},
    )

    context = {"patient": patient, "tasks": tasks} | _patient_context(request, patient=patient)
    return render(request, "patient/patient_details.html", context)


def _patient_context(request: AuthenticatedHttpRequest, patient: Patient | None = None) -> dict[str, Any]:
    """Fetch additional template context required for patient context"""
    return {"patient": patient, "patients": request.user.patient_set.all()}
