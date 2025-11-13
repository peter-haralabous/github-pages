import logging
from typing import TYPE_CHECKING
from typing import Any

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.db.models import Case
from django.db.models import Value
from django.db.models import When
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from guardian.shortcuts import get_objects_for_user

from sandwich.core.models import ListViewType
from sandwich.core.models.custom_attribute import CustomAttribute
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.organization import Organization
from sandwich.core.models.patient import Patient
from sandwich.core.service.custom_attribute_query import annotate_custom_attributes
from sandwich.core.service.custom_attribute_query import apply_filters_with_custom_attributes
from sandwich.core.service.custom_attribute_query import apply_sort_with_custom_attributes
from sandwich.core.service.encounter_service import assign_default_encounter_perms
from sandwich.core.service.invitation_service import get_unaccepted_invitation
from sandwich.core.service.list_preference_service import enrich_filters_with_display_values
from sandwich.core.service.list_preference_service import get_available_columns
from sandwich.core.service.list_preference_service import get_list_view_preference
from sandwich.core.service.list_preference_service import has_unsaved_filters
from sandwich.core.service.list_preference_service import parse_filters_from_query_params
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.core.util.http import validate_sort
from sandwich.providers.views.list_view_state import maybe_redirect_with_saved_filters

if TYPE_CHECKING:
    from uuid import UUID

logger = logging.getLogger(__name__)


class EncounterCreateForm(forms.ModelForm[Encounter]):
    def __init__(self, organization: Organization, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.organization = organization

        # Set up form helper
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Create Encounter", css_class="btn btn-primary", autofocus=True))

    class Meta:
        model = Encounter
        fields = ("patient",)
        widgets = {
            "patient": forms.HiddenInput(),
        }

    def save(self, commit: bool = True) -> Encounter:  # noqa: FBT001, FBT002
        encounter = super().save(commit=False)
        encounter.organization = self.organization
        # TODO-WH: Update the default encounter status below if needed once we have
        # established default statuses for/per organization. Wireframe shows Not set
        # as default, but that's not an option from our EncounterStatus model from the FHIR spec
        encounter.status = EncounterStatus.IN_PROGRESS  # Default status for new encounters
        if commit:
            encounter.save()
        return encounter


@login_required
@authorize_objects(
    [
        ObjPerm(Organization, "organization_id", ["view_organization"]),
        ObjPerm(Encounter, "encounter_id", ["view_encounter"]),
    ]
)
def encounter_details(
    request: AuthenticatedHttpRequest, organization: Organization, encounter: Encounter
) -> HttpResponse:
    patient = encounter.patient
    tasks = encounter.task_set.all()
    other_encounters = patient.encounter_set.exclude(id=encounter.id)
    pending_invitation = get_unaccepted_invitation(patient)

    if not request.user.has_perm("view_invitation", pending_invitation):
        pending_invitation = None

    # Get custom attributes for encounters in this organization
    content_type = ContentType.objects.get_for_model(Encounter)
    custom_attributes = CustomAttribute.objects.filter(
        organization=organization,
        content_type=content_type,
    ).order_by("name")

    # Build a dict of custom attribute values for this encounter
    attribute_values: dict[UUID, Any] = {}
    for attr in custom_attributes:
        values = encounter.attributes.filter(attribute=attr)

        if attr.is_multi:
            # Handle multi-valued attributes - always return a list
            if attr.data_type == CustomAttribute.DataType.DATE:
                attribute_values[attr.id] = [v.value_date for v in values if v.value_date]
            elif attr.data_type == CustomAttribute.DataType.ENUM:
                attribute_values[attr.id] = [v.value_enum.label for v in values if v.value_enum]
            else:
                attribute_values[attr.id] = []
        else:
            # Handle single-valued attributes
            value = values.first()
            if value:
                if attr.data_type == CustomAttribute.DataType.DATE:
                    attribute_values[attr.id] = value.value_date
                elif attr.data_type == CustomAttribute.DataType.ENUM:
                    attribute_values[attr.id] = value.value_enum.label if value.value_enum else None
            else:
                attribute_values[attr.id] = None

    context = {
        "patient": patient,
        "organization": organization,
        "encounter": encounter,
        "other_encounters": other_encounters,
        "tasks": tasks,
        "pending_invitation": pending_invitation,
        "custom_attributes": custom_attributes,
        "attribute_values": attribute_values,
    }
    return render(request, "provider/encounter_details.html", context)


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization"])])
def encounter_list(request: AuthenticatedHttpRequest, organization: Organization) -> HttpResponse:
    request.session["active_organization_id"] = str(organization.id)

    preference = get_list_view_preference(
        request.user,
        organization,
        ListViewType.ENCOUNTER_LIST,
    )

    redirect_response = maybe_redirect_with_saved_filters(request, preference.saved_filters)
    if redirect_response:
        return redirect_response

    filters = parse_filters_from_query_params(request.GET)

    available_columns = get_available_columns(ListViewType.ENCOUNTER_LIST, organization)
    valid_sort_fields = [col["value"] for col in available_columns]

    search = request.GET.get("search", "").strip()
    sort = (
        validate_sort(
            request.GET.get("sort"),
            valid_sort_fields,
        )
        or preference.default_sort
    )
    page = request.GET.get("page", 1)

    logger.debug(
        "Encounter list filters applied",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "search_length": len(search),
            "sort": sort,
            "page": page,
        },
    )

    encounters = get_objects_for_user(
        request.user,
        "view_encounter",
        Encounter.objects.filter(organization=organization).select_related("patient"),
    )

    encounters = encounters.annotate(
        is_active=Case(
            When(status=EncounterStatus.IN_PROGRESS, then=Value(value=True)),
            default=Value(value=False),
        )
    )

    if search:
        encounters = encounters.search(search)  # type: ignore[attr-defined]

    content_type = ContentType.objects.get_for_model(Encounter)
    encounters = annotate_custom_attributes(
        encounters,
        preference.visible_columns,
        organization,
        content_type,
    )

    encounters = apply_filters_with_custom_attributes(
        encounters,
        filters,
        organization,
        content_type,
    )

    if sort:
        encounters = apply_sort_with_custom_attributes(
            encounters,
            sort,
            organization,
            content_type,
        )

    paginator = Paginator(encounters, preference.items_per_page)
    encounters_page = paginator.get_page(page)

    available_index = {c["value"]: c for c in available_columns}
    visible_column_meta = [available_index[v] for v in preference.visible_columns if v in available_index]

    logger.debug(
        "Encounter list results",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "total_count": paginator.count,
            "page_count": len(encounters_page),
            "is_htmx": bool(request.headers.get("HX-Request")),
            "has_saved_preference": preference.pk is not None,
        },
    )

    enriched_filters = enrich_filters_with_display_values(filters, organization, ListViewType.ENCOUNTER_LIST)

    context = {
        "encounters": encounters_page,
        "organization": organization,
        "search": search,
        "sort": sort,
        "page": page,
        "visible_columns": preference.visible_columns,
        "visible_column_meta": visible_column_meta,
        "preference": preference,
        "active_filters": enriched_filters,
        "available_columns": available_columns,
        "has_unsaved_filters": has_unsaved_filters(request, preference),
    }
    if request.headers.get("HX-Request"):
        return render(request, "provider/partials/encounter_list_table.html", context)
    return render(request, "provider/encounter_list.html", context)


@login_required
@authorize_objects(
    [
        ObjPerm(Organization, "organization_id", ["view_organization", "create_encounter"]),
        ObjPerm(Patient, "patient_id", ["view_patient"]),
    ]
)
def encounter_create_select_patient(
    request: AuthenticatedHttpRequest, organization: Organization, patient: Patient
) -> HttpResponse:
    """HTMX endpoint for selecting a patient during encounter creation.

    Returns a modal dialog with patient information and encounter creation form.
    """
    form = EncounterCreateForm(organization, initial={"patient": patient})
    # Set the form action to the encounter_create URL
    form.helper.form_action = reverse(
        "providers:encounter_create",
        kwargs={"organization_id": organization.id},
    )
    context = {
        "organization": organization,
        "patient": patient,
        "form": form,
    }
    return render(request, "provider/partials/encounter_create_modal.html", context)


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization", "create_encounter"])])
def encounter_create(request: AuthenticatedHttpRequest, organization: Organization) -> HttpResponse:
    """Handle POST requests for creating a new encounter from the modal form."""
    if request.method != "POST":
        # This view only handles POST requests now. Redirect to encounter list.
        return HttpResponseRedirect(reverse("providers:encounter_list", kwargs={"organization_id": organization.id}))

    form = EncounterCreateForm(organization, request.POST)
    if form.is_valid():
        encounter = form.save()
        # Assign default permissions to the new encounter
        # form.save() does not call the create method of the
        # underlying model so we need to explictly call
        # assign_default_encounter_perms
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
                kwargs={
                    "encounter_id": encounter.id,
                    "organization_id": organization.id,
                },
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
    # If form is invalid, redirect back to encounter list
    # (In practice, this shouldn't happen as the form is pre-validated in the modal)
    messages.add_message(request, messages.ERROR, "Failed to create encounter. Please try again.")
    return HttpResponseRedirect(reverse("providers:encounter_list", kwargs={"organization_id": organization.id}))


# NOTE-WH: The following patient search is only searching for patients within
# the provider's organization. Should this search need to be expanded to a
# broader/global search, we will need to refactor and potentially permissions. TBC by product.
@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization", "create_encounter"])])
def encounter_create_search(request: AuthenticatedHttpRequest, organization: Organization) -> HttpResponse:
    # HTMX endpoint for searching patients when creating an encounter.
    query = request.GET.get("q", "").strip()
    context_param = request.GET.get("context", "").strip()
    page_size = int(request.GET.get("limit", "10"))
    page = request.GET.get("page", 1)

    if not query:
        paginator = Paginator(Patient.objects.none(), page_size)
    else:
        authorized_patients = get_objects_for_user(
            request.user,
            "view_patient",
            Patient.objects.filter(organization=organization),
        )
        patients_queryset = authorized_patients.search(query)  # type: ignore[attr-defined]
        paginator = Paginator(patients_queryset, page_size)

    logger.debug(
        "Patient search for encounter creation",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "query_length": len(query),
            "total_results": paginator.count,
            "context": context_param,
        },
    )

    patients_page = paginator.get_page(page)

    context = {
        "patients": patients_page,
        "query": query,
        "organization": organization,
        "context": context_param,
    }
    return render(request, "provider/partials/encounter_create_search_results.html", context)
