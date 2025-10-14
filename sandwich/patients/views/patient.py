import logging
from datetime import date
from typing import Any

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div
from crispy_forms.layout import Layout
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
from sandwich.core.validators.date_of_birth import valid_date_of_birth
from sandwich.core.validators.phn import clean_phn
from sandwich.core.validators.phn import phn_attr_for_province
from sandwich.users.models import User

logger = logging.getLogger(__name__)


class PatientEdit(forms.ModelForm[Patient]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["province"].widget.attrs.update(
            {
                "hx-get": reverse("patients:get_phn_validation"),
                "hx-target": "#div_id_phn",
                "hx-trigger": "change",
            }
        )
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div("first_name", "last_name", css_class="flex gap-4"),
            "date_of_birth",
            "province",
            "phn",
            Submit("submit", "Submit"),
        )

    def clean_date_of_birth(self) -> date:
        dob = self.cleaned_data["date_of_birth"]
        return valid_date_of_birth(dob)

    def clean_phn(self):
        """Custom validation for the BC PHN field."""
        province = self.cleaned_data.get("province")
        phn = str(self.cleaned_data.get("phn"))
        if not province or not phn:
            return phn
        cleaned_phn = clean_phn(province, phn)
        if cleaned_phn is not None:
            return cleaned_phn
        error_message = "Invalid phn"
        raise forms.ValidationError(error_message)

    class Meta:
        model = Patient
        fields = ("first_name", "last_name", "date_of_birth", "province", "phn")

        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }


class PatientAdd(forms.ModelForm[Patient]):
    # TODO: add check for duplicate patient
    #       "you already have a patient with this email address/PHN/name"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["province"].widget.attrs.update(
            {
                "hx-get": reverse("patients:get_phn_validation"),
                "hx-target": "#div_id_phn",
                "hx-trigger": "change",
            }
        )
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div("first_name", "last_name", css_class="flex gap-4"),
            "date_of_birth",
            "province",
            "phn",
            Submit("submit", "Submit"),
        )

    def clean_date_of_birth(self) -> date:
        dob = self.cleaned_data["date_of_birth"]
        return valid_date_of_birth(dob)

    def clean_phn(self):
        """Custom validation for the BC PHN field."""
        province = self.cleaned_data.get("province")
        phn = str(self.cleaned_data.get("phn"))
        if not province or not phn:
            return phn
        cleaned_phn = clean_phn(province, phn)
        if cleaned_phn is not None:
            return cleaned_phn
        error_message = "Invalid phn"
        raise forms.ValidationError(error_message)

    def save(self, commit: bool = True, user: User | None = None) -> Patient:  # noqa: FBT001,FBT002
        instance = super().save(commit=False)
        if user is not None:
            instance.user = user
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Patient
        fields = ("first_name", "last_name", "date_of_birth", "province", "phn")
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
def patient_onboarding_add(request: AuthenticatedHttpRequest) -> HttpResponse:
    logger.info("Accessing patient add", extra={"user_id": request.user.id})

    if request.method == "POST":
        logger.info("Processing patient add form", extra={"user_id": request.user.id})
        form = PatientAdd(request.POST)
        if form.is_valid():
            patient = form.save(user=request.user)
            logger.info("Patient created successfully", extra={"user_id": request.user.id, "patient_id": patient.id})
            messages.add_message(request, messages.SUCCESS, "Patient added successfully.")
            return HttpResponseRedirect(reverse("patients:home"))
        logger.warning(
            "Invalid patient add form", extra={"user_id": request.user.id, "form_errors": list(form.errors.keys())}
        )
    else:
        logger.debug("Rendering patient add form", extra={"user_id": request.user.id})
        form = PatientAdd()

    context = {"form": form} | _patient_context(request)
    return render(request, "patient/patient_onboarding_add.html", context)


@login_required
def patient_details(request: AuthenticatedHttpRequest, patient_id: int) -> HttpResponse:
    logger.info("Accessing patient details", extra={"user_id": request.user.id, "patient_id": patient_id})

    patient = get_object_or_404(request.user.patient_set, id=patient_id)

    # TODO-NG: page & sort these lists
    tasks = patient.task_set.all()
    documents = patient.document_set.all()

    logger.debug(
        "Patient details loaded",
        extra={
            "user_id": request.user.id,
            "patient_id": patient_id,
            "task_count": tasks.count(),
            "document_count": documents.count(),
        },
    )

    context = {"patient": patient, "tasks": tasks, "documents": documents} | _patient_context(request, patient=patient)
    return render(request, "patient/patient_details.html", context)


def _patient_context(request: AuthenticatedHttpRequest, patient: Patient | None = None) -> dict[str, Any]:
    """Fetch additional template context required for patient context"""
    return {"patient": patient, "patients": request.user.patient_set.all()}


@login_required
def get_phn_validation(request: AuthenticatedHttpRequest) -> HttpResponse:
    province = request.GET.get("province")

    # Note: being used for patient add/onbboarding, might have to change
    form = PatientEdit()

    attrs = phn_attr_for_province(province)

    # Update the attributes on the form
    form.fields["phn"].widget.attrs.update(attrs)

    logger.debug(
        "Phn pattern results",
        extra={"user_id": request.user.id, "attrs": form.fields["phn"].widget.attrs},
    )

    return render(request, "patient/partials/phn_input.html", {"form": form})
