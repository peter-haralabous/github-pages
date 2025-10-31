"""Views for managing list view preferences."""

import json
import logging
from uuid import UUID

from crispy_forms.helper import FormHelper
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from sandwich.core.models import ListViewPreference
from sandwich.core.models import ListViewType
from sandwich.core.models import Organization
from sandwich.core.models import PreferenceScope
from sandwich.core.service.list_preference_service import get_available_columns
from sandwich.core.service.list_preference_service import get_default_columns
from sandwich.core.service.list_preference_service import get_default_sort
from sandwich.core.service.list_preference_service import get_list_view_preference
from sandwich.core.service.list_preference_service import reset_list_view_preference
from sandwich.core.service.list_preference_service import save_list_view_preference
from sandwich.core.service.list_preference_service import validate_list_type
from sandwich.core.service.organization_service import get_provider_organizations
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


def build_columns_data(
    available_columns: list[dict[str, str]],
    visible_columns: list[str],
) -> list[dict[str, str | bool]]:
    available_lookup = {c["value"]: c for c in available_columns}
    ordered: list[dict[str, str]] = []

    for value in visible_columns:
        col_def = available_lookup.get(value)
        if col_def:
            ordered.append(col_def)

    visible_set = set(visible_columns)
    ordered.extend(col for col in available_columns if col["value"] not in visible_set)

    visible_set = set(visible_columns)
    return [
        {
            "value": col["value"],
            "label": col["label"],
            "checked": col["value"] in visible_set,
        }
        for col in ordered
    ]


@login_required
def list_preference_settings(
    request: AuthenticatedHttpRequest,
    organization_id: UUID,
    list_type: str,
) -> HttpResponse:
    organization = get_object_or_404(
        get_provider_organizations(request.user),
        id=organization_id,
    )

    try:
        list_type_enum = validate_list_type(
            list_type,
            user_id=request.user.id,
            organization_id=organization_id,
        )
    except ValueError:
        return HttpResponse("Invalid list type", status=400)

    preference = get_list_view_preference(request.user, organization, list_type_enum)
    available_columns = get_available_columns(list_type_enum, organization)

    has_user_preference = preference.pk is not None and preference.scope == PreferenceScope.USER

    logger.debug(
        "Loading list preference settings",
        extra={
            "user_id": request.user.id,
            "organization_id": organization_id,
            "list_type": list_type,
            "has_saved_preference": preference.pk is not None,
            "has_user_preference": has_user_preference,
        },
    )

    form = ListPreferenceForm(
        list_type=list_type_enum,
        available_columns=available_columns,
        organization=organization,
        initial={
            "visible_columns": preference.visible_columns,
            "default_sort": preference.default_sort,
            "items_per_page": preference.items_per_page,
        },
    )

    # Order columns so visible ones appear first in saved drag order
    columns_data = build_columns_data(available_columns, preference.visible_columns)

    context = {
        "organization": organization,
        "list_type": list_type,
        "preference": preference,
        "current_sort": preference.default_sort,
        "current_items_per_page": preference.items_per_page,
        "has_user_preference": has_user_preference,
        "form": form,
        "is_org_default": False,
        "columns_data_json": json.dumps(columns_data),
    }

    return render(request, "provider/partials/preference_modal.html", context)


@login_required
@require_POST
def save_list_preference(
    request: AuthenticatedHttpRequest,
    organization_id: UUID,
    list_type: str,
) -> HttpResponse:
    organization = get_object_or_404(
        get_provider_organizations(request.user),
        id=organization_id,
    )

    try:
        list_type_enum = validate_list_type(
            list_type,
            user_id=request.user.id,
            organization_id=organization_id,
        )
    except ValueError:
        return HttpResponse("Invalid list type", status=400)

    available_columns = get_available_columns(list_type_enum, organization)

    form = ListPreferenceForm(
        request.POST,
        list_type=list_type_enum,
        available_columns=available_columns,
        organization=organization,
    )

    if not form.is_valid():
        logger.warning(
            "Invalid form data for list preference",
            extra={
                "user_id": request.user.id,
                "organization_id": organization_id,
                "list_type": list_type,
                "errors": form.errors,
            },
        )
        messages.error(request, "Invalid form data. Please check your selections.")
        return HttpResponse("Invalid form data", status=400)

    visible_columns = form.cleaned_data["visible_columns"]
    default_sort = form.cleaned_data["default_sort"]
    items_per_page = form.cleaned_data["items_per_page"]

    logger.info(
        "Saving user list preference",
        extra={
            "user_id": request.user.id,
            "organization_id": organization_id,
            "list_type": list_type,
            "num_visible_columns": len(visible_columns),
            "items_per_page": items_per_page,
        },
    )

    save_list_view_preference(
        organization=organization,
        list_type=list_type_enum,
        user=request.user,
        visible_columns=visible_columns,
        default_sort=default_sort,
        items_per_page=items_per_page,
    )

    messages.success(request, "Preferences saved successfully")

    return HttpResponse(
        status=200,
        headers={
            "HX-Refresh": "true",
        },
    )


@login_required
@require_POST
def reset_list_preference(
    request: AuthenticatedHttpRequest,
    organization_id: UUID,
    list_type: str,
) -> HttpResponse:
    """
    Reset user's list preferences to organization defaults.
    """
    organization = get_object_or_404(
        get_provider_organizations(request.user),
        id=organization_id,
    )

    try:
        list_type_enum = validate_list_type(
            list_type,
            user_id=request.user.id,
            organization_id=organization_id,
        )
    except ValueError:
        return HttpResponse("Invalid list type", status=400)

    logger.info(
        "Resetting user list preference",
        extra={
            "user_id": request.user.id,
            "organization_id": organization_id,
            "list_type": list_type,
        },
    )

    reset_list_view_preference(organization=organization, list_type=list_type_enum, user=request.user)

    messages.success(request, "Preferences reset to defaults")

    return HttpResponse(
        status=200,
        headers={
            "HX-Refresh": "true",
        },
    )


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["change_organization", "view_organization"])])
def organization_list_preference_settings(
    request: AuthenticatedHttpRequest,
    organization: Organization,
) -> HttpResponse:
    """
    View for organization admins to manage default list preferences.
    """

    logger.debug(
        "Loading organization list preference settings",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
        },
    )

    # Get all list types
    list_types = [
        {
            "value": ListViewType.ENCOUNTER_LIST,
            "label": "Encounter List",
        },
        {
            "value": ListViewType.PATIENT_LIST,
            "label": "Patient List",
        },
    ]

    context = {
        "organization": organization,
        "list_types": list_types,
    }

    return render(request, "provider/organization_list_preferences.html", context)


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["change_organization", "view_organization"])])
def organization_preference_settings_detail(
    request: AuthenticatedHttpRequest,
    organization: Organization,
    list_type: str,
) -> HttpResponse:
    """
    HTMX endpoint to show organization preference settings modal.
    """

    try:
        list_type_enum = validate_list_type(
            list_type,
            user_id=request.user.id,
            organization_id=organization.id,
        )
    except ValueError:
        return HttpResponse("Invalid list type", status=400)

    # Get organization default preference (not user preference)
    org_preference = (
        ListViewPreference.objects.filter(
            organization=organization,
            list_type=list_type_enum,
            scope=PreferenceScope.ORGANIZATION,
            user__isnull=True,
        )
        .select_related("organization")
        .first()
    )

    available_columns = get_available_columns(list_type_enum, organization)

    if org_preference:
        visible_column_values = org_preference.visible_columns
        current_sort = org_preference.default_sort
        current_items_per_page = org_preference.items_per_page
    else:
        visible_column_values = get_default_columns(list_type_enum)
        current_sort = get_default_sort(list_type_enum)
        current_items_per_page = 25

    logger.debug(
        "Loading organization preference settings",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "list_type": list_type,
            "has_org_preference": org_preference is not None,
        },
    )

    form = ListPreferenceForm(
        list_type=list_type_enum,
        available_columns=available_columns,
        organization=organization,
        initial={
            "visible_columns": visible_column_values,
            "default_sort": current_sort,
            "items_per_page": current_items_per_page,
        },
    )

    columns_data = build_columns_data(available_columns, visible_column_values)

    context = {
        "organization": organization,
        "list_type": list_type,
        "preference": org_preference,
        "current_sort": current_sort,
        "current_items_per_page": current_items_per_page,
        "is_org_default": True,
        "form": form,
        "columns_data_json": json.dumps(columns_data),
    }

    return render(request, "provider/partials/preference_modal.html", context)


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["change_organization", "view_organization"])])
@require_POST
def save_organization_preference(
    request: AuthenticatedHttpRequest,
    organization: Organization,
    list_type: str,
) -> HttpResponse:
    """
    Save organization's default list preferences.
    """

    try:
        list_type_enum = validate_list_type(
            list_type,
            user_id=request.user.id,
            organization_id=organization.id,
        )
    except ValueError:
        return HttpResponse("Invalid list type", status=400)

    available_columns = get_available_columns(list_type_enum, organization)

    form = ListPreferenceForm(
        request.POST,
        list_type=list_type_enum,
        available_columns=available_columns,
        organization=organization,
    )

    if not form.is_valid():
        logger.warning(
            "Invalid form data for organization preference",
            extra={
                "user_id": request.user.id,
                "organization_id": organization.id,
                "list_type": list_type,
                "errors": form.errors,
            },
        )
        messages.error(request, "Invalid form data. Please check your selections.")
        return HttpResponse("Invalid form data", status=400)

    visible_columns = form.cleaned_data["visible_columns"]
    default_sort = form.cleaned_data["default_sort"]
    items_per_page = form.cleaned_data["items_per_page"]

    logger.info(
        "Saving organization default list preference",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "list_type": list_type,
            "num_visible_columns": len(visible_columns),
            "items_per_page": items_per_page,
        },
    )

    save_list_view_preference(
        organization=organization,
        list_type=list_type_enum,
        user=None,
        visible_columns=visible_columns,
        default_sort=default_sort,
        items_per_page=items_per_page,
    )

    messages.success(request, "Organization default preferences saved successfully")

    return HttpResponse(
        status=200,
        headers={
            "HX-Refresh": "true",
        },
    )


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["change_organization", "view_organization"])])
@require_POST
def reset_organization_preference(
    request: AuthenticatedHttpRequest,
    organization: Organization,
    list_type: str,
) -> HttpResponse:
    """
    Reset organization's default list preferences to system defaults.
    """

    try:
        list_type_enum = validate_list_type(
            list_type,
            user_id=request.user.id,
            organization_id=organization.id,
        )
    except ValueError:
        return HttpResponse("Invalid list type", status=400)

    logger.info(
        "Resetting organization default list preference",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "list_type": list_type,
        },
    )

    reset_list_view_preference(organization=organization, list_type=list_type_enum, user=None)

    messages.success(request, "Organization preferences reset to system defaults")

    return HttpResponse(
        status=200,
        headers={
            "HX-Refresh": "true",
        },
    )


class ListPreferenceForm(forms.Form):
    """Form for managing list view preferences."""

    visible_columns = forms.MultipleChoiceField(
        required=False,
        widget=forms.MultipleHiddenInput(),
        label=_("Visible Columns"),
    )

    default_sort = forms.ChoiceField(
        required=False,
        label=_("Default Sort"),
        widget=forms.Select(attrs={"class": "select select-bordered"}),
    )

    items_per_page = forms.ChoiceField(
        choices=[
            (10, "10"),
            (25, "25"),
            (50, "50"),
            (100, "100"),
        ],
        initial=25,
        label=_("Items per page"),
        widget=forms.Select(attrs={"class": "select select-bordered"}),
    )

    def __init__(self, *args, list_type: ListViewType, available_columns: list[dict[str, str]], **kwargs) -> None:
        kwargs.pop("organization", None)
        super().__init__(*args, **kwargs)

        column_choices: list[tuple[str, str]] = [(col["value"], col["label"]) for col in available_columns]
        visible_columns_field = self.fields["visible_columns"]
        if isinstance(visible_columns_field, forms.MultipleChoiceField):
            visible_columns_field.choices = column_choices

        sort_choices: list[tuple[str, str]] = [("", str(_("-- No default sort --")))]
        for col in available_columns:
            sort_choices.append((col["value"], f"{col['label']} ({_('Ascending')})"))
            sort_choices.append((f"-{col['value']}", f"{col['label']} ({_('Descending')})"))
        default_sort_field = self.fields["default_sort"]
        if isinstance(default_sort_field, forms.ChoiceField):
            default_sort_field.choices = sort_choices

        self.list_type = list_type
        self.available_column_values = {col["value"] for col in available_columns}

        self.helper = FormHelper()
        self.helper.form_tag = False  # We'll handle the form tag in the template

    def clean_visible_columns(self):
        visible_columns = self.cleaned_data.get("visible_columns", [])

        invalid_columns = [col for col in visible_columns if col not in self.available_column_values]
        if invalid_columns:
            raise forms.ValidationError(
                _("Invalid columns: %(columns)s"),
                params={"columns": ", ".join(invalid_columns)},
            )

        return visible_columns

    def clean_default_sort(self):
        default_sort = self.cleaned_data.get("default_sort", "")

        if not default_sort:
            return ""

        sort_field = default_sort.lstrip("-")

        if sort_field not in self.available_column_values:
            raise forms.ValidationError(_("Invalid sort field: %(field)s"), params={"field": sort_field})

        return default_sort

    def clean_items_per_page(self):
        items_per_page = self.cleaned_data.get("items_per_page", "25")

        try:
            value = int(items_per_page)
        except (ValueError, TypeError):
            return 25
        else:
            if value not in [10, 25, 50, 100]:
                return 25
            return value
