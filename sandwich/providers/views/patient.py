from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Exists
from django.db.models import OuterRef
from django.db.models import Q
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST

from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.organization import Organization
from sandwich.core.models.patient import Patient
from sandwich.core.models.task import Task
from sandwich.core.models.task import TaskStatus
from sandwich.core.service.encounter_service import complete_encounter
from sandwich.core.service.encounter_service import get_current_encounter
from sandwich.core.service.invitation_service import get_pending_invitation
from sandwich.core.service.invitation_service import resend_patient_invitation_email
from sandwich.core.service.organization_service import get_provider_organizations
from sandwich.core.service.task_service import cancel_task
from sandwich.core.service.task_service import send_task_added_email
from sandwich.core.util.http import AuthenticatedHttpRequest


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


@login_required
def patient_details(request: AuthenticatedHttpRequest, organization_id: int, patient_id: int) -> HttpResponse:
    organization = get_object_or_404(get_provider_organizations(request.user), id=organization_id)
    patient = get_object_or_404(organization.patient_set, id=patient_id)
    current_encounter = get_current_encounter(patient)
    tasks = current_encounter.task_set.all() if current_encounter else []
    past_encounters = patient.encounter_set.exclude(status=EncounterStatus.IN_PROGRESS)
    pending_invitation = get_pending_invitation(patient)

    context = {
        "patient": patient,
        "organization": organization,
        "current_encounter": current_encounter,
        "past_encounters": past_encounters,
        "tasks": tasks,
        "pending_invitation": pending_invitation,
    }
    return render(request, "provider/patient_details.html", context)


@login_required
def patient_edit(request: AuthenticatedHttpRequest, organization_id: int, patient_id: int) -> HttpResponse:
    organization = get_object_or_404(get_provider_organizations(request.user), id=organization_id)
    patient = get_object_or_404(organization.patient_set, id=patient_id)

    if request.method == "POST":
        form = PatientEdit(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Patient updated successfully.")
            return HttpResponseRedirect(
                reverse(
                    "providers:patient",
                    kwargs={"patient_id": patient.id, "organization_id": organization.id},
                )
            )
    else:
        form = PatientEdit(instance=patient)

    context = {"form": form, "organization": organization}
    return render(request, "provider/patient_edit.html", context)


@login_required
def patient_add(request: AuthenticatedHttpRequest, organization_id: int) -> HttpResponse:
    organization = get_object_or_404(get_provider_organizations(request.user), id=organization_id)
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


def _validate_sort(sort: str | None, valid_sorts: list[str]) -> str | None:
    if sort is None:
        return None
    field = sort[1:] if sort.startswith("-") else sort
    if field not in valid_sorts:
        return None
    return sort


@login_required
def patient_list(request: AuthenticatedHttpRequest, organization_id: int) -> HttpResponse:
    organization = get_object_or_404(get_provider_organizations(request.user), id=organization_id)

    search = request.GET.get("search", "").strip()
    sort = (
        _validate_sort(
            request.GET.get("sort"),
            ["first_name", "last_name", "email", "date_of_birth", "has_active_encounter", "created_at", "updated_at"],
        )
        or "-updated_at"
    )
    page = request.GET.get("page", 1)
    has_active_encounter_filter = request.GET.get("has_active_encounter", "").lower()

    patients = Patient.objects.filter(organization=organization)
    patients = patients.annotate(
        has_active_encounter=Exists(
            Encounter.objects.filter(patient=OuterRef("pk"), status=EncounterStatus.IN_PROGRESS)
        )
    )

    if has_active_encounter_filter in ("true", "false"):
        patients = patients.filter(has_active_encounter=(has_active_encounter_filter == "true"))

    if search:
        patients = patients.filter(
            Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(phn__icontains=search)
            | Q(email__icontains=search)
        )

    if sort:
        patients = patients.order_by(sort)

    paginator = Paginator(patients, 25)
    patients_page = paginator.get_page(page)

    context = {
        "patients": patients_page,
        "organization": organization,
        "search": search,
        "sort": sort,
        "page": page,
        "has_active_encounter_filter": has_active_encounter_filter,
    }
    if request.headers.get("HX-Request"):
        return render(request, "provider/partials/patient_list_table.html", context)
    return render(request, "provider/patient_list.html", context)


@login_required
@require_POST
def patient_archive(request: AuthenticatedHttpRequest, organization_id: int, patient_id: int) -> HttpResponse:
    organization = get_object_or_404(get_provider_organizations(request.user), id=organization_id)
    patient = get_object_or_404(organization.patient_set, id=patient_id)
    current_encounter = get_current_encounter(patient)

    # in the future we might want to capture _why_ the patient was archived
    # i.e. should status be COMPLETED / CANCELLED / ...
    assert current_encounter is not None, "No current encounter found for patient"
    complete_encounter(current_encounter)

    messages.add_message(request, messages.SUCCESS, "Patient archived successfully.")
    return HttpResponseRedirect(reverse("providers:patient_list", kwargs={"organization_id": organization.id}))


@login_required
@require_POST
def patient_add_task(request: AuthenticatedHttpRequest, organization_id: int, patient_id: int) -> HttpResponse:
    organization = get_object_or_404(get_provider_organizations(request.user), id=organization_id)
    patient = get_object_or_404(organization.patient_set, id=patient_id)

    current_encounter = get_current_encounter(patient)
    if not current_encounter:
        current_encounter = Encounter.objects.create(
            patient=patient, organization=organization, status=EncounterStatus.IN_PROGRESS
        )
    task = Task.objects.create(encounter=current_encounter, patient=patient, status=TaskStatus.REQUESTED)
    send_task_added_email(task)

    messages.add_message(request, messages.SUCCESS, "Task added successfully.")
    return HttpResponseRedirect(
        reverse("providers:patient", kwargs={"organization_id": organization.id, "patient_id": patient.id})
    )


@login_required
@require_POST
def patient_cancel_task(
    request: AuthenticatedHttpRequest, organization_id: int, patient_id: int, task_id: int
) -> HttpResponse:
    organization = get_object_or_404(get_provider_organizations(request.user), id=organization_id)
    patient = get_object_or_404(organization.patient_set, id=patient_id)
    task = get_object_or_404(patient.task_set, id=task_id)

    cancel_task(task)

    messages.add_message(request, messages.SUCCESS, "Task cancelled successfully.")
    return HttpResponseRedirect(
        reverse("providers:patient", kwargs={"organization_id": organization.id, "patient_id": patient.id})
    )


@login_required
@require_POST
def patient_resend_invite(request: AuthenticatedHttpRequest, organization_id: int, patient_id: int) -> HttpResponse:
    organization = get_object_or_404(get_provider_organizations(request.user), id=organization_id)
    patient = get_object_or_404(organization.patient_set, id=patient_id)

    assert patient.user is None, "Patient already has a user"
    resend_patient_invitation_email(patient)

    messages.add_message(request, messages.SUCCESS, "Invitation resent successfully.")
    return HttpResponseRedirect(
        reverse("providers:patient", kwargs={"organization_id": organization.id, "patient_id": patient.id})
    )
