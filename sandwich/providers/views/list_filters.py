"""Views for managing list view filters."""

import logging
from typing import Any
from typing import cast
from urllib.parse import urlencode
from uuid import UUID

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML
from crispy_forms.layout import Div
from crispy_forms.layout import Field
from crispy_forms.layout import Layout
from crispy_forms.layout import Submit
from crispy_forms.utils import render_crispy_form
from django import forms
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from sandwich.core.models import CustomAttribute
from sandwich.core.models import CustomAttributeEnum
from sandwich.core.models import ListViewPreference
from sandwich.core.models import ListViewType
from sandwich.core.models import Organization
from sandwich.core.models import PreferenceScope
from sandwich.core.models.list_preference import DEFAULT_ITEMS_PER_PAGE
from sandwich.core.service.list_preference_service import encode_filters_to_url_params
from sandwich.core.service.list_preference_service import get_available_columns
from sandwich.core.service.list_preference_service import get_list_view_preference
from sandwich.core.service.list_preference_service import parse_filters_from_query_params
from sandwich.core.service.list_preference_service import save_filters_to_preference
from sandwich.core.service.list_preference_service import save_list_view_preference
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.core.validators.list_preference_validators import validate_and_clean_filters

logger = logging.getLogger(__name__)

FILTER_MODE_PARAM = "filter_mode"
FILTER_MODE_CUSTOM = "custom"
PAGE_PARAM = "page"

LIST_TYPE_URL_MAP = {
    "encounter_list": "providers:encounter_list",
    "patient_list": "providers:patient_list",
}


def _build_date_range_filter(request: AuthenticatedHttpRequest) -> dict[str, str]:
    """Extract date range values from request."""
    date_range = {}
    if start := request.POST.get("start"):
        date_range["start"] = start
    if end := request.POST.get("end"):
        date_range["end"] = end
    return date_range


def _build_custom_attribute_filter(request: AuthenticatedHttpRequest, attribute: CustomAttribute) -> dict[str, Any]:
    """Build filter configuration for a custom attribute."""
    if attribute.data_type == CustomAttribute.DataType.ENUM:
        if values := request.POST.getlist("values"):
            return {"type": "enum", "operator": "in", "values": values}

    if attribute.data_type == CustomAttribute.DataType.DATE:
        operator = request.POST.get("operator", "range")
        if operator == "range":
            if date_range := _build_date_range_filter(request):
                return {"type": "date", "operator": "range", **date_range}
        elif value := request.POST.get("value"):
            return {"type": "date", "operator": operator, "value": value}

    return {}


def _build_model_field_date_filter(request: AuthenticatedHttpRequest, field_id: str) -> dict[str, Any]:
    """Build date filter for model field."""
    operator = request.POST.get("operator", "range")

    if operator == "range":
        if date_range := _build_date_range_filter(request):
            return {field_id: date_range}
    elif value := request.POST.get("value"):
        return {field_id: {"operator": operator, "value": value}}

    return {}


def _build_model_field_filter(
    request: AuthenticatedHttpRequest, field_id: str, field_type: str | None
) -> dict[str, Any]:
    """Build filter configuration for a standard model field."""
    if field_type == "date":
        return _build_model_field_date_filter(request, field_id)

    if field_type == "enum":
        if values := request.POST.getlist("values"):
            return {field_id: values}
    elif field_type == "boolean":
        if value := request.POST.get("value"):
            return {field_id: value}
    else:
        if values := request.POST.getlist("values"):
            return {field_id: values}
        if value := request.POST.get("value"):
            return {field_id: value}

    return {}


def _get_custom_attribute(field_id: str, organization: Organization, list_type_enum: ListViewType) -> CustomAttribute:
    """Get custom attribute by field_id (expects 'custom:UUID' format)."""
    attribute_id = field_id.removeprefix("custom:")
    try:
        attr_uuid = UUID(attribute_id)
    except ValueError as e:
        raise ValueError("Invalid attribute_id") from e

    if not (content_type := list_type_enum.get_content_type()):
        raise ValueError("Invalid content type")

    try:
        return CustomAttribute.objects.get(
            id=attr_uuid,
            organization=organization,
            content_type=content_type,
        )
    except CustomAttribute.DoesNotExist as e:
        raise ValueError("Attribute not found") from e


def _build_redirect_url(list_type: str, organization: Organization, params: dict) -> str:
    """Build redirect URL with query parameters."""
    if not (url_name := LIST_TYPE_URL_MAP.get(list_type)):
        raise ValueError(f"Unsupported list type: {list_type}")

    url = reverse(url_name, kwargs={"organization_id": organization.id})
    if params:
        # Ensure all values are lists for consistent URL encoding
        list_params = {k: v if isinstance(v, list) else [v] for k, v in params.items()}
        url += f"?{urlencode(list_params, doseq=True)}"
    return url


def _get_filter_keys_to_remove(field_id: str) -> list[str]:
    """Get list of URL parameter keys to remove for a given field."""
    try:
        attr_uuid = UUID(field_id)
        attr_id = str(attr_uuid).replace("-", "_")
        prefix = f"filter_attr_{attr_id}"
    except ValueError:
        prefix = f"filter_{field_id}"

    return [prefix, f"{prefix}_start", f"{prefix}_end"]


def _ensure_user_preference(
    request: AuthenticatedHttpRequest,
    organization: Organization,
    list_type_enum: ListViewType,
    preference: ListViewPreference,
) -> ListViewPreference:
    """Ensure preference is a saved user-scoped preference, creating one if needed."""
    if preference.pk and preference.scope == PreferenceScope.USER and preference.user_id == request.user.id:
        return preference

    return save_list_view_preference(
        organization=organization,
        list_type=list_type_enum,
        user=request.user,
        visible_columns=list(preference.visible_columns or ListViewPreference.get_default_columns(list_type_enum)),
        default_sort=preference.default_sort or ListViewPreference.get_default_sort(list_type_enum),
        items_per_page=preference.items_per_page or DEFAULT_ITEMS_PER_PAGE,
        saved_filters=preference.saved_filters or {},
    )


def _render_custom_attribute_filter(request: AuthenticatedHttpRequest, attribute: CustomAttribute) -> HttpResponse:
    """Render filter control for custom attribute."""
    if attribute.data_type == CustomAttribute.DataType.ENUM:
        enum_values = list(CustomAttributeEnum.objects.filter(attribute=attribute).order_by("label"))
        return render(
            request,
            "provider/partials/filter_enum_control.html",
            {"attribute": attribute, "form": EnumFilterForm(choices=enum_values)},
        )

    if attribute.data_type == CustomAttribute.DataType.DATE:
        return render(
            request,
            "provider/partials/filter_date_control.html",
            {"attribute": attribute, "form": DateFilterForm()},
        )

    return HttpResponse("Unsupported data type", status=400)


def _render_model_field_filter(
    request: AuthenticatedHttpRequest, field_id: str, list_type: ListViewType
) -> HttpResponse:
    """Render filter control for standard model field."""
    if not (field_type := list_type.get_field_type(field_id)):
        return HttpResponse("Unknown field", status=400)

    if field_type == "date":
        return render(
            request,
            "provider/partials/filter_date_control.html",
            {"field_id": field_id, "field_type": field_type, "form": DateFilterForm()},
        )

    if field_type == "enum":
        choices = list_type.get_field_choices(field_id)
        return render(
            request,
            "provider/partials/filter_enum_control.html",
            {"field_id": field_id, "field_type": field_type, "form": EnumFilterForm(choices=choices)},
        )

    return HttpResponse(render_crispy_form(TextFilterForm()))


class FilterFieldSelectForm(forms.Form):
    """Form for selecting which field to filter on."""

    field_id = forms.ChoiceField(
        label=_("Field"),
        required=True,
        widget=forms.RadioSelect(attrs={"class": "radio radio-xs"}),
        help_text=_("Select a field below. Then configure filter details."),
    )

    def __init__(self, standard_fields: list, custom_attributes: list, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        choices = self._build_field_choices(standard_fields, custom_attributes)
        field_id_field = cast("forms.ChoiceField", self.fields["field_id"])
        field_id_field.choices = choices

        self.helper = self._build_form_helper(choices)

    def _build_field_choices(self, standard_fields: list, custom_attributes: list) -> list[tuple[str, str]]:
        """Build flat choice list combining standard fields and custom attributes."""
        choices = [(field["value"], field["label"]) for field in standard_fields]
        choices.extend((f"custom:{attr.id}", attr.name) for attr in custom_attributes)
        return choices or [("", str(_("No available fields")))]

    def _build_form_helper(self, choices: list[tuple[str, str]]) -> FormHelper:
        """Build crispy forms helper with custom layout."""
        helper = FormHelper(self)
        helper.form_id = "filter-form"
        helper.attrs = {"hx-swap": "none"}
        helper.form_method = "post"

        header_html = f'<h4 class="text-sm font-medium mb-2">{_("Select Field")}</h4>'
        radios_html = self._build_radio_buttons_html(choices)
        cancel_html = f'<form method="dialog"><button class="btn">{_("Cancel")}</button></form>'

        helper.layout = Layout(
            Div(HTML(header_html + radios_html), css_class="mb-4"),
            Div(css_id="filter-controls", css_class="mt-5 mb-4"),
            Div(
                HTML(cancel_html),
                Submit("submit", _("Apply Filter"), css_class="btn btn-primary"),
                css_class="modal-action",
            ),
        )
        return helper

    def _build_radio_buttons_html(self, choices: list[tuple[str, str]]) -> str:
        """Build HTML for radio button group."""
        container_open = '<div class="filter flex-wrap gap-2 items-center" id="field-filter-button-group">'
        reset_label = str(_("Reset field selection"))
        reset_button = (
            '<button type="button" class="btn btn-square btn-sm filter-reset" '
            f'aria-label="{reset_label}" id="field-filter-reset">\u00d7</button>'
        )
        parts = [container_open, reset_button]

        for value, label in choices:
            radio_input = (
                '<input class="btn btn-sm field-radio-item" type="radio" '
                f'name="field_id" value="{value}" aria-label="{label}" '
                f'data-label="{label}" data-value="{value}" required>'
            )
            parts.append(radio_input)

        parts.append("</div>")
        return "".join(parts)


class DateFilterForm(forms.Form):
    """Form for date range or comparison filters."""

    operator = forms.ChoiceField(
        label=_("Filter type"),
        choices=[
            ("exact", _("Exact date")),
            ("range", _("Date range")),
            ("gte", _("On or after")),
            ("lte", _("On or before")),
        ],
        initial="exact",
        widget=forms.Select(
            attrs={
                "class": "select select-bordered mb-3",
                "id": "date-operator",
                "aria-label": "Select date filter type",
            }
        ),
    )
    start = forms.DateField(
        label=_("Start date"),
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "input input-bordered mb-2",
                "placeholder": "YYYY-MM-DD",
                "aria-describedby": "start-date-help",
            }
        ),
    )
    end = forms.DateField(
        label=_("End date"),
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "input input-bordered",
                "placeholder": "YYYY-MM-DD",
                "aria-describedby": "end-date-help",
            }
        ),
    )
    value = forms.DateField(
        label=_("Date"),
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "input input-bordered",
                "placeholder": "YYYY-MM-DD",
                "aria-describedby": "single-date-help",
            }
        ),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field("operator"),
            Div(
                Field("start"),
                Field("end"),
                css_id="date-range-inputs",
            ),
            Div(Field("value"), css_id="date-single-input", css_class="hidden"),
            Div(
                HTML(f'<div class="text-sm font-medium text-base-content/70 mb-2">{_("Quick select:")}</div>'),
                HTML(
                    '<div class="grid grid-cols-2 gap-2">'
                    f'<button type="button" class="btn btn-sm btn-outline" data-preset="7">'
                    f"{_('Last 7 days')}</button>"
                    f'<button type="button" class="btn btn-sm btn-outline" data-preset="30">'
                    f"{_('Last 30 days')}</button>"
                    f'<button type="button" class="btn btn-sm btn-outline" data-preset="month">'
                    f"{_('This month')}</button>"
                    f'<button type="button" class="btn btn-sm btn-outline" data-preset="year">'
                    f"{_('This year')}</button>"
                    "</div>"
                ),
                css_id="date-preset-buttons",
                css_class="mt-4",
            ),
        )

    def clean(self) -> dict[str, Any]:
        """Validate date range."""
        cleaned_data = super().clean()
        if cleaned_data is None:
            return {}

        operator = cleaned_data.get("operator")
        start = cleaned_data.get("start")
        end = cleaned_data.get("end")

        if operator == "range" and start and end and start > end:
            self.add_error("end", _("End date must be after start date"))

        return cleaned_data


class EnumFilterForm(forms.Form):
    """Form for enum/multi-select filters (custom attributes and standard model fields)."""

    values = forms.MultipleChoiceField(
        label=_("Select values"),
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox checkbox-sm"}),
    )

    def __init__(self, choices: list, *args, **kwargs) -> None:
        """Initialize form with choices."""
        super().__init__(*args, **kwargs)

        values_field = cast("forms.MultipleChoiceField", self.fields["values"])

        if choices and hasattr(choices[0], "value"):
            values_field.choices = [(ev.value, ev.label) for ev in choices]
            self.enum_values = choices
        else:
            values_field.choices = choices
            self.enum_choices = choices

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class TextFilterForm(forms.Form):
    """Form for text input filters."""

    value = forms.CharField(
        label=_("Filter value"),
        required=True,
        widget=forms.TextInput(attrs={"class": "input input-bordered", "placeholder": _("Enter value...")}),
        help_text=_("Enter the value to filter by. For multiple values, separate with commas."),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization"])])
def show_filter_modal(
    request: AuthenticatedHttpRequest,
    organization: Organization,
    list_type: str,
) -> HttpResponse:
    """Render the filter modal for adding a new filter."""
    try:
        list_type_enum = ListViewType(list_type)
    except ValueError:
        logger.warning("Invalid list type for filter modal", extra={"list_type": list_type})
        return HttpResponse("Invalid list type", status=400)

    if not (content_type := list_type_enum.get_content_type()):
        return HttpResponse("Invalid content type", status=400)

    standard_fields = list_type_enum.get_column_definitions()
    custom_attributes = list(
        CustomAttribute.objects.filter(organization=organization, content_type=content_type).order_by("name")
    )

    form = FilterFieldSelectForm(standard_fields=standard_fields, custom_attributes=custom_attributes)
    post_url = reverse(
        "providers:apply_filter",
        kwargs={"organization_id": organization.id, "list_type": list_type},
    )
    if query := request.GET.urlencode():
        post_url += f"?{query}"
    form.helper.attrs["hx-post"] = post_url

    context = {"organization": organization, "list_type": list_type, "form": form}
    return render(request, "provider/partials/filter_modal.html", context)


def _process_filter_from_request(
    request: AuthenticatedHttpRequest,
    field_id: str,
    organization: Organization,
    list_type_enum: ListViewType,
) -> dict[str, Any]:
    """Process and build filters from request data."""
    filters: dict[str, Any] = {"custom_attributes": {}, "model_fields": {}}

    if field_id.startswith("custom:"):
        attribute = _get_custom_attribute(field_id, organization, list_type_enum)
        if not (attr_filter := _build_custom_attribute_filter(request, attribute)):
            raise ValueError("No filter values provided")
        filters["custom_attributes"][str(attribute.id)] = attr_filter
    else:
        available_columns = get_available_columns(list_type_enum, organization)
        valid_field_ids = {col["value"] for col in available_columns if not col.get("is_custom")}
        if field_id not in valid_field_ids:
            raise ValueError("Invalid field for this list type")

        field_type = list_type_enum.get_field_type(field_id)
        if not (model_filters := _build_model_field_filter(request, field_id, field_type)):
            raise ValueError("No filter values provided")
        filters["model_fields"].update(model_filters)

    return filters


@login_required
@require_POST
@authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization"])])
def apply_filter(
    request: AuthenticatedHttpRequest,
    organization: Organization,
    list_type: str,
) -> HttpResponse:
    """Apply a filter by redirecting to URL with filter parameters."""
    try:
        list_type_enum = ListViewType(list_type)
    except ValueError:
        logger.warning("Invalid list type for apply filter", extra={"list_type": list_type})
        return HttpResponse("Invalid list type", status=400)

    if not (field_id := request.POST.get("field_id")):
        return HttpResponse("Missing field_id", status=400)

    try:
        filters = _process_filter_from_request(request, field_id, organization, list_type_enum)
        validate_and_clean_filters(filters, organization, list_type_enum)
    except ValueError as e:
        logger.warning("Filter processing failed", extra={"user_id": request.user.id, "error": str(e)})
        return HttpResponse(str(e), status=400)

    params = dict(request.GET)
    params.update(encode_filters_to_url_params(filters))

    for param in ["search", "sort"]:
        if value := (request.POST.get(param) or request.GET.get(param)):
            params[param] = value

    params[PAGE_PARAM] = "1"
    params[FILTER_MODE_PARAM] = FILTER_MODE_CUSTOM

    try:
        redirect_url = _build_redirect_url(list_type, organization, params)
    except ValueError as e:
        return HttpResponse(str(e), status=400)

    logger.info(
        "Filter applied via URL redirect",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "list_type": list_type,
            "field_id": field_id,
        },
    )
    response = HttpResponse(status=200)
    response["HX-Redirect"] = redirect_url
    return response


@login_required
@require_POST
@authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization"])])
def remove_filter(
    request: AuthenticatedHttpRequest,
    organization: Organization,
    list_type: str,
    field_id: str,
) -> HttpResponse:
    """Remove a specific filter by redirecting to URL without that filter."""
    try:
        ListViewType(list_type)
    except ValueError:
        logger.warning("Invalid list type for remove filter", extra={"list_type": list_type})
        return HttpResponse("Invalid list type", status=400)

    params = dict(request.GET)
    for key in _get_filter_keys_to_remove(field_id):
        params.pop(key, None)

    params[FILTER_MODE_PARAM] = FILTER_MODE_CUSTOM
    params[PAGE_PARAM] = "1"

    try:
        redirect_url = _build_redirect_url(list_type, organization, params)
    except ValueError as e:
        return HttpResponse(str(e), status=400)

    logger.info(
        "Filter removed via URL redirect",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "list_type": list_type,
            "field_id": field_id,
        },
    )
    response = HttpResponse(status=200)
    response["HX-Redirect"] = redirect_url
    return response


@login_required
@require_POST
@authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization"])])
def clear_all_filters(
    request: AuthenticatedHttpRequest,
    organization: Organization,
    list_type: str,
) -> HttpResponse:
    """Clear all filters by redirecting to URL without any filter parameters."""
    try:
        ListViewType(list_type)
    except ValueError:
        logger.warning("Invalid list type for clear filters", extra={"list_type": list_type})
        return HttpResponse("Invalid list type", status=400)

    params = {param: request.GET[param] for param in ["search", "sort"] if param in request.GET}
    params[FILTER_MODE_PARAM] = FILTER_MODE_CUSTOM
    params[PAGE_PARAM] = "1"

    try:
        redirect_url = _build_redirect_url(list_type, organization, params)
    except ValueError as e:
        return HttpResponse(str(e), status=400)

    logger.info(
        "All filters cleared via URL redirect",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "list_type": list_type,
        },
    )
    response = HttpResponse(status=200)
    response["HX-Redirect"] = redirect_url
    return response


@login_required
@require_POST
@authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization"])])
def save_current_filters(
    request: AuthenticatedHttpRequest,
    organization: Organization,
    list_type: str,
) -> HttpResponse:
    """Save current URL filters to user preference."""
    try:
        list_type_enum = ListViewType(list_type)
    except ValueError:
        logger.warning("Invalid list type for save filters", extra={"list_type": list_type})
        return HttpResponse("Invalid list type", status=400)

    preference = get_list_view_preference(request.user, organization, list_type_enum)
    preference = _ensure_user_preference(request, organization, list_type_enum, preference)

    filters = parse_filters_from_query_params(request.GET)

    try:
        save_filters_to_preference(preference, filters)
        logger.info(
            "Saved current filters to preference",
            extra={
                "user_id": request.user.id,
                "organization_id": organization.id,
                "list_type": list_type,
            },
        )
    except ValueError as e:
        logger.warning("Filter validation failed", extra={"user_id": request.user.id, "error": str(e)})
        return HttpResponse(str(e), status=400)

    if preference.pk:
        preference.refresh_from_db()

    # Preserve search and sort, but clear filter params (they're now in user preference)
    params = {param: request.GET[param] for param in ["search", "sort"] if param in request.GET}

    try:
        redirect_url = _build_redirect_url(list_type, organization, params)
    except ValueError as e:
        return HttpResponse(str(e), status=400)

    response = HttpResponse(status=200)
    response["HX-Redirect"] = redirect_url
    return response


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization"])])
def get_filter_options(
    request: AuthenticatedHttpRequest,
    organization: Organization,
) -> HttpResponse:
    """Get filter options for a specific field (renders control partial)."""
    field_id = request.GET.get("field_id")
    list_type_str = request.GET.get("list_type")

    if not field_id or not list_type_str:
        return HttpResponse("Missing field_id or list_type", status=400)

    try:
        list_type = ListViewType(list_type_str)
    except ValueError:
        return HttpResponse("Invalid list_type", status=400)

    if field_id.startswith("custom:"):
        attribute_id_str = field_id.removeprefix("custom:")
        try:
            attr_uuid = UUID(attribute_id_str)
            attribute = CustomAttribute.objects.get(id=attr_uuid, organization=organization)
            return _render_custom_attribute_filter(request, attribute)
        except (ValueError, CustomAttribute.DoesNotExist):
            return HttpResponse("Invalid or not found attribute", status=404)

    return _render_model_field_filter(request, field_id, list_type)
