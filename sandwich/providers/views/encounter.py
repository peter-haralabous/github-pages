import logging
from typing import TYPE_CHECKING
from typing import Any

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Case
from django.db.models import Value
from django.db.models import When
from django.http import HttpResponse
from django.http.response import HttpResponseBadRequest
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from guardian.shortcuts import get_objects_for_user

from sandwich.core.models import CustomAttributeValue
from sandwich.core.models import ListViewType
from sandwich.core.models.custom_attribute import CustomAttribute
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.organization import Organization
from sandwich.core.models.patient import Patient
from sandwich.core.service.custom_attribute_query import annotate_custom_attributes
from sandwich.core.service.custom_attribute_query import apply_filters_with_custom_attributes
from sandwich.core.service.custom_attribute_query import apply_sort_with_custom_attributes
from sandwich.core.service.custom_attribute_query import update_custom_attribute
from sandwich.core.service.encounter_service import assign_default_encounter_perms
from sandwich.core.service.encounter_service import complete_encounter
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
from sandwich.providers.forms.inline_edit import FormContext
from sandwich.providers.forms.inline_edit import InlineEditForm
from sandwich.providers.forms.inline_edit import create_inline_edit_form
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


def _format_attribute_value(attr: CustomAttribute, values: list) -> str | None:
    """
    Format custom attribute values for display.

    Returns formatted string value, or None if no values exist
    """
    if not values:
        return None

    if attr.is_multi:
        # Handle multi-valued attributes - return comma-separated string
        if attr.data_type == CustomAttribute.DataType.DATE:
            formatted = [str(v.value_date) for v in values if v.value_date]
        elif attr.data_type == CustomAttribute.DataType.ENUM:
            formatted = [v.value_enum.label for v in values if v.value_enum]
        else:
            return None
        return ", ".join(formatted) if formatted else None
    # Handle single-valued attributes
    value = values[0]
    if attr.data_type == CustomAttribute.DataType.DATE:
        return str(value.value_date) if value.value_date else None
    if attr.data_type == CustomAttribute.DataType.ENUM:
        return value.value_enum.label if value.value_enum else None
    return None


def _format_attributes(encounter: Encounter, custom_attributes: list[CustomAttribute]) -> list[dict[str, Any]]:
    """
    Build a simplified representation of custom attributes with their values.

    Returns list of dicts with 'name' and 'value' keys for template rendering
    """
    # Prefetch all attribute values for this encounter to avoid N+1 queries
    attribute_values_qs = encounter.attributes.select_related("value_enum").all()

    # Group values by attribute ID
    values_by_attr: dict[UUID, list] = {}
    for value in attribute_values_qs:
        if value.attribute_id not in values_by_attr:
            values_by_attr[value.attribute_id] = []
        values_by_attr[value.attribute_id].append(value)

    # Build formatted attribute list
    formatted = []
    for attr in custom_attributes:
        values = values_by_attr.get(attr.id, [])
        formatted_value = _format_attribute_value(attr, values)
        formatted.append(
            {
                "name": attr.name,
                "value": formatted_value,
            }
        )

    return formatted


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
    custom_attributes = list(
        CustomAttribute.objects.filter(
            organization=organization,
            content_type=content_type,
        ).order_by("name")
    )

    # Format attributes with their values for display
    formatted_attributes = _format_attributes(encounter, custom_attributes)

    context = {
        "patient": patient,
        "organization": organization,
        "encounter": encounter,
        "other_encounters": other_encounters,
        "tasks": tasks,
        "pending_invitation": pending_invitation,
        "formatted_attributes": formatted_attributes,
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


def _get_custom_attribute_value_display(
    encounter: Encounter, attribute: CustomAttribute, content_type: ContentType
) -> str:
    """Get display value for a custom attribute."""
    try:
        attr_value = CustomAttributeValue.objects.get(
            attribute=attribute,
            content_type=content_type,
            object_id=encounter.id,
        )
        if attribute.data_type == CustomAttribute.DataType.ENUM and attr_value.value_enum:
            return attr_value.value_enum.label
        if attribute.data_type == CustomAttribute.DataType.DATE and attr_value.value_date:
            return attr_value.value_date.strftime("%Y-%m-%d")
    except CustomAttributeValue.DoesNotExist:
        return "—"
    return "—"


def _get_custom_attribute(field_name: str, organization: Organization) -> CustomAttribute | None:
    """Get a custom attribute by ID if it exists."""
    try:
        return CustomAttribute.objects.get(
            id=field_name,
            organization=organization,
            content_type=ContentType.objects.get_for_model(Encounter),
        )
    except (CustomAttribute.DoesNotExist, ValueError, ValidationError):
        return None


def _get_field_display_value(encounter: Encounter, field_name: str, organization: Organization) -> str:
    """Helper to get the display value for a field.

    Args:
        encounter: The encounter instance
        field_name: The field name (e.g., 'status' or custom attribute field_id)
        organization: The organization context

    Returns:
        The formatted display value or a placeholder
    """
    if field_name == "status":
        return encounter.get_status_display() or "—"

    # Custom attribute
    attribute = _get_custom_attribute(field_name, organization)
    if not attribute:
        return "—"

    content_type = ContentType.objects.get_for_model(Encounter)
    return _get_custom_attribute_value_display(encounter, attribute, content_type)


def _build_custom_attribute_form_context(encounter: Encounter, attribute: CustomAttribute) -> FormContext | None:
    """Build form context for custom attribute editing.

    Returns:
        Context dict with choices, current_value, field_type, and field_label.
        None if attribute data type is not supported.
    """
    field_label = attribute.name
    content_type = ContentType.objects.get_for_model(Encounter)

    if attribute.data_type == CustomAttribute.DataType.ENUM:
        enum_set = getattr(attribute, "customattributeenum_set", None)
        choices = [(str(enum.id), str(enum.label)) for enum in enum_set.all()] if enum_set else []
        field_type = "select"

        try:
            attr_value = CustomAttributeValue.objects.get(
                attribute=attribute,
                content_type=content_type,
                object_id=encounter.id,
            )
            value_enum_id = getattr(attr_value, "value_enum_id", None)
            current_value = str(value_enum_id) if value_enum_id else None
        except CustomAttributeValue.DoesNotExist:
            current_value = None

    elif attribute.data_type == CustomAttribute.DataType.DATE:
        choices = []
        field_type = "date"

        try:
            attr_value = CustomAttributeValue.objects.get(
                attribute=attribute,
                content_type=content_type,
                object_id=encounter.id,
            )
            current_value = attr_value.value_date.strftime("%Y-%m-%d") if attr_value.value_date else None
        except CustomAttributeValue.DoesNotExist:
            current_value = None
    else:
        return None

    return {
        "choices": choices,
        "current_value": current_value,
        "field_type": field_type,
        "field_label": field_label,
    }


def _build_edit_form_context(encounter: Encounter, field_name: str, organization: Organization) -> FormContext | None:
    """Build context for the inline edit form.

    Returns:
        Context dict with choices, current_value, field_type, and field_label.
        None if field_name is invalid.
    """
    choices: list[tuple[str, str]] = []
    current_value: str | None = None
    field_type: str
    field_label: str

    if field_name == "status":
        choices = [(status.value, str(status.label)) for status in EncounterStatus]
        current_value = encounter.status.value
        field_type = "select"
        field_label = "Status"

    else:
        # Custom attribute
        attribute = _get_custom_attribute(field_name, organization)
        if not attribute:
            return None

        return _build_custom_attribute_form_context(encounter, attribute)

    return {
        "choices": choices,
        "current_value": current_value,
        "field_type": field_type,
        "field_label": field_label,
    }


@login_required
@authorize_objects(
    [
        ObjPerm(Organization, "organization_id", ["view_organization"]),
        ObjPerm(Encounter, "encounter_id", ["view_encounter", "change_encounter"]),
    ]
)
def encounter_edit_field(
    request: AuthenticatedHttpRequest, organization: Organization, encounter: Encounter, field_name: str
) -> HttpResponse:
    """Handle GET/POST for editing a specific encounter field inline."""
    form_context = _build_edit_form_context(encounter, field_name, organization)
    if not form_context:
        return HttpResponseBadRequest("Invalid field name")

    form_action = reverse(
        "providers:encounter_edit_field",
        kwargs={
            "organization_id": organization.id,
            "encounter_id": encounter.id,
            "field_name": field_name,
        },
    )

    cell_id = f"encounter-{encounter.id}-{field_name}"

    if request.method == "GET":
        form = create_inline_edit_form(
            form_context=form_context,
            field_name=field_name,
            form_action=form_action,
            hx_target=f"#{cell_id}",
        )

        display_value = _get_field_display_value(encounter, field_name, organization)

        context = {
            "encounter": encounter,
            "organization": organization,
            "field_name": field_name,
            "form": form,
            "field_type": form_context["field_type"],
            "display_value": display_value,
        }

        return render(request, "provider/partials/inline_edit_form.html", context)

    # POST request - update field
    form = create_inline_edit_form(
        form_context=form_context,
        field_name=field_name,
        form_action=form_action,
        hx_target=cell_id,
        data=request.POST,
    )

    if not form.is_valid():
        return _render_form_with_errors(request, encounter, organization, field_name, form)

    new_value = form.cleaned_data.get("value", "")
    if isinstance(new_value, str):
        new_value = new_value.strip()

    if not _handle_field_update(encounter, field_name, str(new_value), organization, form):
        return _render_form_with_errors(request, encounter, organization, field_name, form)

    logger.info(
        "Encounter field updated via inline edit",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "encounter_id": encounter.id,
            "field_name": field_name,
            "new_value": new_value,
        },
    )

    display_value = _get_field_display_value(encounter, field_name, organization)

    context = {
        "encounter": encounter,
        "organization": organization,
        "field_name": field_name,
        "display_value": display_value,
        "cell_id": cell_id,
        "can_edit": True,
        "oob": False,
    }

    logger.info(
        "Returning inline edit display",
        extra={
            "cell_id": cell_id,
            "display_value": display_value,
            "oob": False,
        },
    )

    return render(request, "provider/partials/inline_edit_display.html", context)


def _render_form_with_errors(
    request: AuthenticatedHttpRequest,
    encounter: Encounter,
    organization: Organization,
    field_name: str,
    form: InlineEditForm,
) -> HttpResponse:
    """Render the inline edit form with error messages."""
    display_value = _get_field_display_value(encounter, field_name, organization)
    field_type = form.field_type

    context = {
        "encounter": encounter,
        "organization": organization,
        "field_name": field_name,
        "form": form,
        "field_type": field_type,
        "display_value": display_value,
        "errors": form.errors.get("value", ["Invalid value"])[0] if form.errors else None,
    }
    return HttpResponseBadRequest(render(request, "provider/partials/inline_edit_form.html", context).content)


def _handle_field_update(
    encounter: Encounter,
    field_name: str,
    new_value: str,
    organization: Organization,
    form: InlineEditForm,
) -> bool:
    """Update the specified field. Returns True if successful, False otherwise."""
    if field_name == "status":
        if not _update_model_field(encounter, field_name, new_value):
            form.add_error("value", f"Invalid {field_name} value")
            return False
        return True

    attribute = _get_custom_attribute(field_name, organization)
    if not attribute:
        return False
    if not update_custom_attribute(encounter, attribute, new_value):
        form.add_error("value", f"Invalid {attribute.data_type} value")
        return False
    return True


def _update_model_field(encounter: Encounter, field_name: str, new_value: str) -> bool:
    """Update a model field (status). Returns True if successful."""
    if field_name == "status":
        try:
            encounter.status = EncounterStatus(new_value)
            encounter.save()
        except ValueError:
            return False
        else:
            return True

    return False


@login_required
@authorize_objects(
    [
        ObjPerm(Organization, "organization_id", ["view_organization"]),
        ObjPerm(Encounter, "encounter_id", ["view_encounter", "change_encounter"]),
    ]
)
def encounter_archive(
    request: AuthenticatedHttpRequest, organization: Organization, encounter: Encounter
) -> HttpResponse:
    if request.method != "POST":
        return HttpResponseRedirect(reverse("providers:encounter_list", kwargs={"organization_id": organization.id}))

    if encounter.status != EncounterStatus.COMPLETED:
        complete_encounter(encounter, request.user)
        message = "Encounter archived successfully."
        logger.info(
            "Encounter archived successfully",
            extra={"user_id": request.user.id, "organization_id": organization.id, "encounter_id": encounter.id},
        )
    else:
        encounter.status = EncounterStatus.IN_PROGRESS
        encounter.ended_at = None
        encounter.save()
        message = "Encounter unarchived successfully."
        logger.info(
            "Encounter unarchived successfully",
            extra={"user_id": request.user.id, "organization_id": organization.id, "encounter_id": encounter.id},
        )

    messages.add_message(request, messages.SUCCESS, message)
    return HttpResponseRedirect(reverse("providers:encounter_list", kwargs={"organization_id": organization.id}))
