from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST

from sandwich.core.models import Organization
from sandwich.core.models import Patient
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.task import Task
from sandwich.core.models.task import TaskStatus


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

    def save(self, commit: bool = True, organization: Organization | None = None) -> Patient:  # noqa: FBT001,FBT002
        instance = super().save(commit=False)
        if organization is not None:
            instance.organization = organization
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Patient
        fields = ("first_name", "last_name", "email", "phn", "date_of_birth")
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }


def _current_encounter(patient: Patient) -> Encounter | None:
    return patient.encounter_set.filter(status=EncounterStatus.IN_PROGRESS).first()


@login_required
def patient_details(request: HttpRequest, organization_id: int, patient_id: int) -> HttpResponse:
    organization = get_object_or_404(Organization, id=organization_id)
    patient = get_object_or_404(organization.patient_set, id=patient_id)
    current_encounter = _current_encounter(patient)
    tasks = current_encounter.task_set.all() if current_encounter else []

    context = {
        "patient": patient,
        "organization": organization,
        "current_encounter": current_encounter,
        "tasks": tasks,
    }
    return render(request, "provider/patient_details.html", context)


@login_required
def patient_edit(request: HttpRequest, organization_id: int, patient_id: int) -> HttpResponse:
    organization = get_object_or_404(Organization, id=organization_id)
    patient = get_object_or_404(organization.patient_set, id=patient_id)

    if request.method == "POST":
        form = PatientEdit(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Patient updated successfully.")
            return HttpResponseRedirect(
                reverse(
                    "providers:patient_edit",
                    kwargs={"patient_id": patient.id, "organization_id": organization.id},
                )
            )
    else:
        form = PatientEdit(instance=patient)

    context = {"form": form, "organization": organization}
    return render(request, "provider/patient_edit.html", context)


@login_required
def patient_add(request: HttpRequest, organization_id: int) -> HttpResponse:
    organization = get_object_or_404(Organization, id=organization_id)
    if request.method == "POST":
        form = PatientAdd(request.POST)
        if form.is_valid():
            patient = form.save(organization=organization)
            Encounter.objects.create(patient=patient, organization=organization, status=EncounterStatus.IN_PROGRESS)
            messages.add_message(request, messages.SUCCESS, "Patient added successfully.")
            return HttpResponseRedirect(
                reverse("providers:patient", kwargs={"patient_id": patient.id, "organization_id": organization.id})
            )
    else:
        form = PatientAdd()

    context = {"form": form, "organization": organization}
    return render(request, "provider/patient_add.html", context)


@login_required
def patient_list(request: HttpRequest, organization_id: int) -> HttpResponse:
    organization = get_object_or_404(Organization, id=organization_id)
    patients = list(Patient.objects.filter(organization=organization))

    context = {"patients": patients, "organization": organization}
    return render(request, "provider/patient_list.html", context)


@login_required
@require_POST
def patient_archive(request: HttpRequest, organization_id: int, patient_id: int) -> HttpResponse:
    organization = get_object_or_404(Organization, id=organization_id)
    patient = get_object_or_404(organization.patient_set, id=patient_id)
    current_encounter = _current_encounter(patient)

    # in the future we might want to capture _why_ the patient was archived
    # i.e. should status be COMPLETED / CANCELLED / ...
    assert current_encounter is not None, "No current encounter found for patient"
    current_encounter.status = EncounterStatus.COMPLETED
    current_encounter.save()

    # cancel all outstanding tasks
    for task in current_encounter.task_set.all():
        if task.active:
            task.status = TaskStatus.CANCELLED
            task.save()

    messages.add_message(request, messages.SUCCESS, "Patient archived successfully.")
    return HttpResponseRedirect(reverse("providers:patient_list", kwargs={"organization_id": organization.id}))


@login_required
@require_POST
def patient_add_task(request: HttpRequest, organization_id: int, patient_id: int) -> HttpResponse:
    organization = get_object_or_404(Organization, id=organization_id)
    patient = get_object_or_404(organization.patient_set, id=patient_id)

    current_encounter = _current_encounter(patient)
    if not current_encounter:
        current_encounter = Encounter.objects.create(
            patient=patient, organization=organization, status=EncounterStatus.IN_PROGRESS
        )
    Task.objects.create(encounter=current_encounter, patient=patient, status=TaskStatus.REQUESTED)

    messages.add_message(request, messages.SUCCESS, "Task added successfully.")
    return HttpResponseRedirect(
        reverse("providers:patient", kwargs={"organization_id": organization.id, "patient_id": patient.id})
    )


@login_required
@require_POST
def patient_cancel_task(request: HttpRequest, organization_id: int, patient_id: int, task_id: int) -> HttpResponse:
    organization = get_object_or_404(Organization, id=organization_id)
    patient = get_object_or_404(organization.patient_set, id=patient_id)
    task = get_object_or_404(patient.task_set, id=task_id)

    task.status = TaskStatus.CANCELLED
    task.save()

    messages.add_message(request, messages.SUCCESS, "Task cancelled successfully.")
    return HttpResponseRedirect(
        reverse("providers:patient", kwargs={"organization_id": organization.id, "patient_id": patient.id})
    )
