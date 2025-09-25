import logging
from uuid import UUID

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Exists
from django.db.models import OuterRef
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse

from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.organization import Organization
from sandwich.core.service.invitation_service import get_pending_invitation
from sandwich.core.service.organization_service import get_provider_organizations
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.core.util.http import validate_sort

logger = logging.getLogger(__name__)


def build_encounter_form_class(organization: Organization) -> type[forms.ModelForm[Encounter]]:
    patient_status_choices = [(s.value, s.label) for s in organization.patient_statuses]
    patient_status_choices.insert(0, ("", "—"))

    # TODO-NG: there's got to be a better way to pass the patient status choices through
    #          without creating a new class for each organization
    class EncounterForm(forms.ModelForm[Encounter]):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.helper = FormHelper()
            self.helper.add_input(Submit("submit", "Submit"))

        class Meta:
            model = Encounter
            fields = ("patient_status",)
            widgets = {
                "patient_status": forms.Select(choices=patient_status_choices),
            }

    return EncounterForm


@login_required
def encounter_details(request: AuthenticatedHttpRequest, organization_id: UUID, encounter_id: UUID) -> HttpResponse:
    organization = get_object_or_404(get_provider_organizations(request.user), id=organization_id)
    encounter = get_object_or_404(organization.encounter_set, id=encounter_id)
    patient = encounter.patient
    tasks = encounter.task_set.all()
    other_encounters = patient.encounter_set.exclude(id=encounter_id)
    pending_invitation = get_pending_invitation(patient)

    EncounterForm = build_encounter_form_class(organization)  # noqa: N806
    if request.method == "POST":
        current_encounter_form = EncounterForm(request.POST, instance=encounter)
        if current_encounter_form.is_valid():
            current_encounter_form.save()
            logger.info(
                "Encounter updated successfully",
                extra={
                    "user_id": request.user.id,
                    "organization_id": organization_id,
                    "patient_id": patient.id,
                    "encounter_id": encounter.id,
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
                "organization_id": organization_id,
                "patient_id": patient.id,
                "encounter_id": encounter.id,
                "form_errors": list(current_encounter_form.errors.keys()),
            },
        )
    else:
        logger.debug(
            "Rendering encounter form",
            extra={
                "user_id": request.user.id,
                "organization_id": organization_id,
                "patient_id": patient.id,
                "encounter_id": encounter.id,
            },
        )
        current_encounter_form = EncounterForm(instance=encounter)

    context = {
        "patient": patient,
        "organization": organization,
        "encounter": encounter,
        "encounter_form": current_encounter_form,
        "other_encounters": other_encounters,
        "tasks": tasks,
        "pending_invitation": pending_invitation,
    }
    return render(request, "provider/encounter_details.html", context)


@login_required
def encounter_list(request: AuthenticatedHttpRequest, organization_id: UUID) -> HttpResponse:
    organization = get_object_or_404(get_provider_organizations(request.user), id=organization_id)

    search = request.GET.get("search", "").strip()
    sort = (
        validate_sort(
            request.GET.get("sort"),
            [
                "patient__first_name",
                "patient__last_name",
                "patient__email",
                "patient__date_of_birth",
                "patient_status",
                "created_at",
                "updated_at",
            ],
        )
        or "-updated_at"
    )
    page = request.GET.get("page", 1)
    active_filter = request.GET.get("active", "").lower()
    patient_status_filter = request.GET.get("patient_status", "").lower()

    logger.debug(
        "Encounter list filters applied",
        extra={
            "user_id": request.user.id,
            "organization_id": organization_id,
            "search_length": len(search),
            "sort": sort,
            "page": page,
            "active_filter": active_filter,
            "patient_status_filter": patient_status_filter,
        },
    )

    encounters = Encounter.objects.filter(organization=organization)
    encounters = encounters.annotate(
        has_active_encounter=Exists(
            Encounter.objects.filter(patient=OuterRef("pk"), status=EncounterStatus.IN_PROGRESS)
        )
    )

    if active_filter == "true":
        encounters = encounters.filter(status=EncounterStatus.IN_PROGRESS)
    elif active_filter == "false":
        encounters = encounters.exclude(status=EncounterStatus.IN_PROGRESS)

    if patient_status_filter:
        encounters = encounters.filter(patient_status=patient_status_filter)

    if search:
        encounters = encounters.search(search)  # type: ignore[attr-defined]

    if sort:
        encounters = encounters.order_by(sort)

    paginator = Paginator(encounters, 25)
    encounters_page = paginator.get_page(page)

    logger.debug(
        "Encounter list results",
        extra={
            "user_id": request.user.id,
            "organization_id": organization_id,
            "total_count": paginator.count,
            "page_count": len(encounters_page),
            "is_htmx": bool(request.headers.get("HX-Request")),
        },
    )

    context = {
        "encounters": encounters_page,
        "organization": organization,
        "search": search,
        "sort": sort,
        "page": page,
        "active_filter": active_filter,
        "patient_status_filter": patient_status_filter,
    }
    if request.headers.get("HX-Request"):
        return render(request, "provider/partials/encounter_list_table.html", context)
    return render(request, "provider/encounter_list.html", context)
