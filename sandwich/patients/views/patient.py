from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib import messages
from django.http import HttpRequest
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse

from sandwich.core.models import Patient


class PatientEdit(forms.ModelForm[Patient]):
    def __init__(self, *args, **kwargs):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit"))

    class Meta:
        model = Patient
        fields = ("first_name", "last_name", "email", "phn", "date_of_birth")
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }


def patient(request: HttpRequest, pk: int) -> HttpResponse:
    patient = get_object_or_404(Patient, id=pk)
    if request.method == "POST":
        form = PatientEdit(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Patient updated successfully.")
            return HttpResponseRedirect(reverse("patient", kwargs={"pk": pk}))
    else:
        form = PatientEdit(instance=patient)

    context = {"form": form}
    return render(request, "patient/patient_edit.html", context)


def patient_add(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = PatientAdd(request.POST)
        if form.is_valid():
            patient = form.save()
            messages.add_message(request, messages.SUCCESS, "Patient added successfully.")
            return HttpResponseRedirect(reverse("patients:patient", kwargs={"pk": patient.id}))
    else:
        form = PatientAdd()

    context = {"form": form}
    return render(request, "patient/patient_add.html", context)
