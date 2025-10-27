import logging
from datetime import date

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div
from crispy_forms.layout import Layout
from crispy_forms.layout import Submit
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Exists
from django.db.models import OuterRef
from django.db.models import QuerySet
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST
from guardian.shortcuts import get_objects_for_user

from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.organization import Organization
from sandwich.core.models.patient import Patient
from sandwich.core.models.task import Task
from sandwich.core.models.task import TaskStatus
from sandwich.core.service.encounter_service import assign_default_encounter_perms
from sandwich.core.service.encounter_service import complete_encounter
from sandwich.core.service.encounter_service import get_current_encounter
from sandwich.core.service.invitation_service import get_unaccepted_invitation
from sandwich.core.service.invitation_service import resend_patient_invitation_email
from sandwich.core.service.organization_service import get_provider_organizations
from sandwich.core.service.patient_service import maybe_patient_name
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.service.task_service import assign_default_task_perms
from sandwich.core.service.task_service import cancel_task
from sandwich.core.service.task_service import send_task_added_email
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.core.util.http import validate_sort
from sandwich.core.validators.date_of_birth import valid_date_of_birth
from sandwich.providers.views.encounter import build_encounter_form_class

logger = logging.getLogger(__name__)


class PatientEdit(forms.ModelForm[Patient]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div("first_name", "last_name", css_class="flex gap-4"),
            "date_of_birth",
            "province",
            "phn",
            "email",
            Submit("submit", "Submit"),
        )

    def clean_date_of_birth(self) -> date:
        dob = self.cleaned_data["date_of_birth"]
        return valid_date_of_birth(dob)

    class Meta:
        model = Patient
        fields = ("first_name", "last_name", "date_of_birth", "province", "phn", "email")
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }


class PatientAdd(forms.ModelForm[Patient]):
    # TODO: add check for duplicate patient
    #       "you already have a patient with this email address/PHN/name"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div("first_name", "last_name", css_class="flex gap-4"),
            "date_of_birth",
            "province",
            "phn",
            "email",
            Submit("submit", "Submit"),
        )

    def clean_date_of_birth(self) -> date:
        dob = self.cleaned_data["date_of_birth"]
        return valid_date_of_birth(dob)

    def save(self, commit: bool = True, organization: Organization | None = None) -> Patient:  # noqa: FBT001,FBT002
        instance = super().save(commit=False)
        if organization is not None:
            instance.organization = organization
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Patient
        fields = ("first_name", "last_name", "date_of_birth", "province", "phn", "email")
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }


@login_required
@authorize_objects(
    [ObjPerm(Patient, "patient_id", ["view_patient"]), ObjPerm(Organization, "organization_id", ["view_organization"])]
)
def patient_details(request: AuthenticatedHttpRequest, organization: Organization, patient: Patient) -> HttpResponse:
    logger.info(
        "Accessing provider patient details",
        extra={"user_id": request.user.id, "organization_id": organization.id, "patient_id": patient.id},
    )

    current_encounter = get_current_encounter(patient)
    tasks = current_encounter.task_set.all() if current_encounter else []
    past_encounters = patient.encounter_set.exclude(status=EncounterStatus.IN_PROGRESS)
    pending_invitation = get_unaccepted_invitation(patient)

    logger.debug(
        "Patient details loaded",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "patient_id": patient.id,
            "has_current_encounter": bool(current_encounter),
            "task_count": len(list(tasks)),
            "past_encounter_count": past_encounters.count(),
            "has_pending_invitation": bool(pending_invitation),
        },
    )

    EncounterForm = build_encounter_form_class(organization)  # noqa: N806
    if current_encounter:
        if request.method == "POST":
            logger.info(
                "Processing encounter update form",
                extra={
                    "user_id": request.user.id,
                    "organization_id": organization.id,
                    "patient_id": patient.id,
                    "encounter_id": current_encounter.id,
                },
            )
            current_encounter_form = EncounterForm(request.POST, instance=current_encounter)
            if current_encounter_form.is_valid():
                current_encounter_form.save()
                logger.info(
                    "Encounter updated successfully",
                    extra={
                        "user_id": request.user.id,
                        "organization_id": organization.id,
                        "patient_id": patient.id,
                        "encounter_id": current_encounter.id,
                    },
                )
                messages.add_message(request, messages.SUCCESS, "Encounter updated successfully.")
                return HttpResponseRedirect(
                    reverse(
                        "providers:patient",
                        kwargs={"patient_id": patient.id, "organization_id": organization.id},
                    )
                )
            logger.warning(
                "Invalid encounter update form",
                extra={
                    "user_id": request.user.id,
                    "organization_id": organization.id,
                    "patient_id": patient.id,
                    "encounter_id": current_encounter.id,
                    "form_errors": list(current_encounter_form.errors.keys()),
                },
            )
        else:
            logger.debug(
                "Rendering encounter form",
                extra={
                    "user_id": request.user.id,
                    "organization_id": organization.id,
                    "patient_id": patient.id,
                    "encounter_id": current_encounter.id,
                },
            )
            current_encounter_form = EncounterForm(instance=current_encounter)
    else:
        current_encounter_form = None

    context = {
        "patient": patient,
        "organization": organization,
        "current_encounter": current_encounter,
        "current_encounter_form": current_encounter_form,
        "past_encounters": past_encounters,
        "tasks": tasks,
        "pending_invitation": pending_invitation,
    }
    return render(request, "provider/patient_details.html", context)


@login_required
@authorize_objects(
    [
        ObjPerm(Patient, "patient_id", ["view_patient", "change_patient"]),
        ObjPerm(Organization, "organization_id", ["view_organization"]),
    ]
)
def patient_edit(request: AuthenticatedHttpRequest, organization: Organization, patient: Patient) -> HttpResponse:
    logger.info(
        "Accessing provider patient edit",
        extra={"user_id": request.user.id, "organization_id": organization.id, "patient_id": patient.id},
    )

    if request.method == "POST":
        logger.info(
            "Processing provider patient edit form",
            extra={"user_id": request.user.id, "organization_id": organization.id, "patient_id": patient.id},
        )
        form = PatientEdit(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            logger.info(
                "Provider patient updated successfully",
                extra={"user_id": request.user.id, "organization_id": organization.id, "patient_id": patient.id},
            )
            messages.add_message(request, messages.SUCCESS, "Patient updated successfully.")
            return HttpResponseRedirect(
                reverse(
                    "providers:patient",
                    kwargs={"patient_id": patient.id, "organization_id": organization.id},
                )
            )
        logger.warning(
            "Invalid provider patient edit form",
            extra={
                "user_id": request.user.id,
                "organization_id": organization.id,
                "patient_id": patient.id,
                "form_errors": list(form.errors.keys()),
            },
        )
    else:
        logger.debug(
            "Rendering provider patient edit form",
            extra={"user_id": request.user.id, "organization_id": organization.id, "patient_id": patient.id},
        )
        form = PatientEdit(instance=patient)

    context = {"form": form, "organization": organization}
    return render(request, "provider/patient_edit.html", context)


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization", "create_encounter"])])
def patient_add(request: AuthenticatedHttpRequest, organization: Organization) -> HttpResponse:
    logger.info(
        "Accessing provider patient add", extra={"user_id": request.user.id, "organization_id": organization.id}
    )

    if request.method == "POST":
        logger.info(
            "Processing provider patient add form",
            extra={"user_id": request.user.id, "organization_id": organization.id},
        )
        form = PatientAdd(request.POST)
        if form.is_valid():
            patient = form.save(organization=organization)
            # Check if this patient was created via the encounter flow (by checking for a GET param or session flag)
            if request.GET.get("from_encounter"):
                # Redirect to encounter create page with patient preselected
                return HttpResponseRedirect(
                    reverse("providers:encounter_create", kwargs={"organization_id": organization.id})
                    + f"?patient_id={patient.id}"
                )
            # Default: create encounter and redirect to patient details
            encounter = Encounter.objects.create(
                patient=patient, organization=organization, status=EncounterStatus.IN_PROGRESS
            )
            assign_default_encounter_perms(encounter)
            logger.info(
                "Provider patient and encounter created successfully",
                extra={
                    "user_id": request.user.id,
                    "organization_id": organization.id,
                    "patient_id": patient.id,
                    "encounter_id": encounter.id,
                },
            )
            messages.add_message(request, messages.SUCCESS, "Patient added successfully.")
            return HttpResponseRedirect(
                reverse("providers:patient", kwargs={"patient_id": patient.id, "organization_id": organization.id})
            )
        logger.warning(
            "Invalid provider patient add form",
            extra={
                "user_id": request.user.id,
                "organization_id": organization.id,
                "form_errors": list(form.errors.keys()),
            },
        )
    else:
        maybe_name = maybe_patient_name(request.GET.get("maybe_name", ""))
        if maybe_name:
            logger.debug(
                "Pre-filling patient form with parsed name",
                extra={"user_id": request.user.id, "organization_id": organization.id, "has_parsed_name": True},
            )
            form = PatientAdd()
            form.fields["first_name"].initial = maybe_name[0]
            form.fields["last_name"].initial = maybe_name[1]
        else:
            logger.debug(
                "Rendering empty provider patient add form",
                extra={"user_id": request.user.id, "organization_id": organization.id},
            )
            form = PatientAdd()

    context = {"form": form, "organization": organization}
    return render(request, "provider/patient_add.html", context)


@login_required
def patient_list(request: AuthenticatedHttpRequest, organization_id: int) -> HttpResponse:
    logger.info("Accessing patient list", extra={"user_id": request.user.id, "organization_id": organization_id})

    organization = get_object_or_404(get_provider_organizations(request.user), id=organization_id)

    search = request.GET.get("search", "").strip()
    sort = (
        validate_sort(
            request.GET.get("sort"),
            ["first_name", "last_name", "email", "date_of_birth", "has_active_encounter", "created_at", "updated_at"],
        )
        or "-updated_at"
    )
    page = request.GET.get("page", 1)
    has_active_encounter_filter = request.GET.get("has_active_encounter", "").lower()
    patient_status_filter = request.GET.get("patient_status", "").lower()

    logger.debug(
        "Patient list filters applied",
        extra={
            "user_id": request.user.id,
            "organization_id": organization_id,
            "search_length": len(search),
            "sort": sort,
            "page": page,
            "has_active_encounter_filter": has_active_encounter_filter,
            "patient_status_filter": patient_status_filter,
        },
    )

    provider_patients: QuerySet = get_objects_for_user(request.user, "core.view_patient")
    patients = provider_patients.filter(organization=organization)

    provider_encounters: QuerySet = get_objects_for_user(request.user, "core.view_encounter")
    patients = patients.annotate(
        has_active_encounter=Exists(
            provider_encounters.filter(patient=OuterRef("pk"), status=EncounterStatus.IN_PROGRESS)
        )
    )

    if has_active_encounter_filter in ("true", "false"):
        patients = patients.filter(has_active_encounter=(has_active_encounter_filter == "true"))

    if patient_status_filter:
        patients = patients.filter(encounter__patient_status=patient_status_filter)

    if search:
        patients = patients.search(search)

    if sort:
        patients = patients.order_by(sort)

    paginator = Paginator(patients, 25)
    patients_page = paginator.get_page(page)

    logger.debug(
        "Patient list results",
        extra={
            "user_id": request.user.id,
            "organization_id": organization_id,
            "total_count": paginator.count,
            "page_count": len(patients_page),
            "is_htmx": bool(request.headers.get("HX-Request")),
        },
    )

    context = {
        "patients": patients_page,
        "organization": organization,
        "search": search,
        "sort": sort,
        "page": page,
        "has_active_encounter_filter": has_active_encounter_filter,
        "patient_status_filter": patient_status_filter,
    }
    if request.headers.get("HX-Request"):
        return render(request, "provider/partials/patient_list_table.html", context)
    return render(request, "provider/patient_list.html", context)


@login_required
@require_POST
def patient_archive(request: AuthenticatedHttpRequest, organization_id: int, patient_id: int) -> HttpResponse:
    logger.info(
        "Archiving patient",
        extra={"user_id": request.user.id, "organization_id": organization_id, "patient_id": patient_id},
    )

    organization = get_object_or_404(get_provider_organizations(request.user), id=organization_id)
    patient = get_object_or_404(organization.patient_set, id=patient_id)
    current_encounter = get_current_encounter(patient)
    if not current_encounter or not request.user.has_perm("change_encounter", current_encounter):
        return HttpResponseNotFound()

    # in the future we might want to capture _why_ the patient was archived
    # i.e. should status be COMPLETED / CANCELLED / ...
    assert current_encounter is not None, "No current encounter found for patient"
    complete_encounter(current_encounter)

    logger.info(
        "Patient archived successfully",
        extra={
            "user_id": request.user.id,
            "organization_id": organization_id,
            "patient_id": patient_id,
            "encounter_id": current_encounter.id,
        },
    )

    messages.add_message(request, messages.SUCCESS, "Patient archived successfully.")
    return HttpResponseRedirect(reverse("providers:patient_list", kwargs={"organization_id": organization.id}))


@login_required
@require_POST
@authorize_objects(
    [
        ObjPerm(Organization, "organization_id", ["view_organization", "create_encounter", "create_invitation"]),
        ObjPerm(Patient, "patient_id", ["view_patient", "create_task"]),
    ]
)
def patient_add_task(request: AuthenticatedHttpRequest, organization: Organization, patient: Patient) -> HttpResponse:
    logger.info(
        "Adding task to patient",
        extra={"user_id": request.user.id, "organization_id": organization.id, "patient_id": patient.id},
    )

    current_encounter = get_current_encounter(patient)
    if current_encounter and not request.user.has_perm("view_encounter", current_encounter):
        return HttpResponseNotFound()

    if not current_encounter:
        current_encounter = Encounter.objects.create(
            patient=patient, organization=organization, status=EncounterStatus.IN_PROGRESS
        )
        assign_default_encounter_perms(current_encounter)
        logger.debug(
            "Created new encounter for task",
            extra={
                "user_id": request.user.id,
                "organization_id": organization.id,
                "patient_id": patient.id,
                "encounter_id": current_encounter.id,
            },
        )

    task = Task.objects.create(encounter=current_encounter, patient=patient, status=TaskStatus.REQUESTED)
    assign_default_task_perms(task)
    send_task_added_email(task)

    logger.info(
        "Task added successfully",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "patient_id": patient.id,
            "task_id": task.id,
            "encounter_id": current_encounter.id,
        },
    )

    messages.add_message(request, messages.SUCCESS, "Task added successfully.")
    return HttpResponseRedirect(
        reverse("providers:patient", kwargs={"organization_id": organization.id, "patient_id": patient.id})
    )


@login_required
@require_POST
def patient_cancel_task(
    request: AuthenticatedHttpRequest, organization_id: int, patient_id: int, task_id: int
) -> HttpResponse:
    logger.info(
        "Cancelling patient task",
        extra={
            "user_id": request.user.id,
            "organization_id": organization_id,
            "patient_id": patient_id,
            "task_id": task_id,
        },
    )

    organization = get_object_or_404(get_provider_organizations(request.user), id=organization_id)
    patient = get_object_or_404(organization.patient_set, id=patient_id)
    task = get_object_or_404(patient.task_set, id=task_id)

    cancel_task(task)

    logger.info(
        "Task cancelled successfully",
        extra={
            "user_id": request.user.id,
            "organization_id": organization_id,
            "patient_id": patient_id,
            "task_id": task_id,
        },
    )

    messages.add_message(request, messages.SUCCESS, "Task cancelled successfully.")
    return HttpResponseRedirect(
        reverse("providers:patient", kwargs={"organization_id": organization.id, "patient_id": patient.id})
    )


@login_required
@require_POST
def patient_resend_invite(request: AuthenticatedHttpRequest, organization_id: int, patient_id: int) -> HttpResponse:
    logger.info(
        "Resending patient invitation",
        extra={"user_id": request.user.id, "organization_id": organization_id, "patient_id": patient_id},
    )

    organization = get_object_or_404(get_provider_organizations(request.user), id=organization_id)
    patient = get_object_or_404(organization.patient_set, id=patient_id)

    assert patient.user is None, "Patient already has a user"
    resend_patient_invitation_email(patient)

    logger.info(
        "Patient invitation resent successfully",
        extra={"user_id": request.user.id, "organization_id": organization_id, "patient_id": patient_id},
    )

    messages.add_message(request, messages.SUCCESS, "Invitation resent successfully.")
    return HttpResponseRedirect(
        reverse("providers:patient", kwargs={"organization_id": organization.id, "patient_id": patient.id})
    )
