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
from sandwich.core.models.patient import Patient
from sandwich.core.service.encounter_service import assign_default_encounter_perms
from sandwich.core.service.invitation_service import get_unaccepted_invitation
from sandwich.core.service.organization_service import get_provider_organizations
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.core.util.http import validate_sort

logger = logging.getLogger(__name__)


class EncounterCreateForm(forms.ModelForm[Encounter]):
    def __init__(self, organization: Organization, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.organization = organization

        # Set up patient status choices
        patient_status_choices = [(s.value, s.label) for s in (organization.patient_statuses or [])]
        patient_status_choices.insert(0, ("", "—"))
        self.fields["patient_status"].widget = forms.Select(choices=patient_status_choices)

        # Set up form helper
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Create Interaction", css_class="btn btn-primary"))

    class Meta:
        model = Encounter
        fields = ("patient", "patient_status")
        widgets = {
            "patient": forms.HiddenInput(),
        }

    def save(self, commit: bool = True) -> Encounter:  # noqa: FBT001, FBT002
        encounter = super().save(commit=False)
        encounter.organization = self.organization
        # TODO-WH: Update the default encounter status below if needed once we have
        # established default statuses for/per organization. Wireframe shows Not set
        # as default, but that's not an option from our EncounterStatus model from the FHIR spec
        encounter.status = EncounterStatus.UNKNOWN  # Default status for new encounters
        if commit:
            encounter.save()
        return encounter


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
    pending_invitation = get_unaccepted_invitation(patient)

    if not request.user.has_perm("view_invitation", pending_invitation):
        pending_invitation = None

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
    request.session["active_organization_id"] = str(organization.id)
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


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization"])])
def encounter_create(request: AuthenticatedHttpRequest, organization: Organization) -> HttpResponse:
    """View for creating a new encounter."""
    if request.method == "POST":
        form = EncounterCreateForm(organization, request.POST)
        if form.is_valid():
            encounter = form.save()
            # Assign default permissions to the new encounter
            assign_default_encounter_perms(encounter)
            logger.info(
                "Encounter created successfully",
                extra={
                    "user_id": request.user.id,
                    "organization_id": organization.id,
                    "patient_id": encounter.patient.id,
                    "encounter_id": encounter.id,
                },
            )
            messages.add_message(request, messages.SUCCESS, "Encounter created successfully.")
            return HttpResponseRedirect(
                reverse(
                    "providers:encounter",
                    kwargs={"encounter_id": encounter.id, "organization_id": organization.id},
                )
            )
        logger.warning(
            "Invalid encounter creation form",
            extra={
                "user_id": request.user.id,
                "organization_id": organization.id,
                "form_errors": list(form.errors.keys()),
            },
        )
    else:
        form = EncounterCreateForm(organization)

    context = {
        "organization": organization,
        "form": form,
    }

    return render(request, "provider/encounter_create.html", context)


# NOTE-WH: The following patient search is only searching for patients within
# the provider's organization. Should this search need to be expanded to a
# broader/global search, we will need to refactor and potentially permissions. TBC by product.
@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization", "create_encounter"])])
def encounter_create_search(request: AuthenticatedHttpRequest, organization: Organization) -> HttpResponse:
    """HTMX endpoint for searching patients when creating an encounter."""
    query = request.GET.get("q", "").strip()
    page_size = int(request.GET.get("limit", "10"))
    page = request.GET.get("page", 1)

    if not query:
        paginator = Paginator(Patient.objects.none(), page_size)
    else:
        patients_queryset = Patient.objects.filter(organization=organization).search(query)  # type: ignore[attr-defined]
        paginator = Paginator(patients_queryset, page_size)

    logger.debug(
        "Patient search for encounter creation",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "query_length": len(query),
            "total_results": paginator.count,
        },
    )

    patients_page = paginator.get_page(page)

    context = {
        "patients": patients_page,
        "query": query,
    }
    return render(request, "provider/partials/encounter_create_search_results.html", context)
