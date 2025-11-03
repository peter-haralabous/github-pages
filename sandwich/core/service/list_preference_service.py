import logging
from typing import Any
from uuid import UUID

from django.http import HttpRequest
from guardian.shortcuts import assign_perm

from sandwich.core.models import CustomAttribute
from sandwich.core.models import ListViewPreference
from sandwich.core.models import ListViewType
from sandwich.core.models import Organization
from sandwich.core.models import PreferenceScope
from sandwich.core.models.role import RoleName
from sandwich.core.validators.list_preference_validators import validate_and_clean_filters
from sandwich.users.models import User

logger = logging.getLogger(__name__)

DEFAULT_ITEMS_PER_PAGE = 25


def assign_default_listviewpreference_perms(preference: ListViewPreference) -> None:
    """
    Assign default permissions for a ListViewPreference.

    Organization-level preferences get permissions for owner, admin, and staff roles.
    User-level preferences get permissions for the owning user only.
    """
    if preference.scope == PreferenceScope.ORGANIZATION:
        roles = preference.organization.role_set.exclude(name=RoleName.PATIENT)
        for role in roles:
            assign_perm("view_listviewpreference", role.group, preference)
            if role.name in [RoleName.OWNER, RoleName.ADMIN]:
                assign_perm("change_listviewpreference", role.group, preference)
                assign_perm("delete_listviewpreference", role.group, preference)

    elif preference.scope == PreferenceScope.USER and preference.user:
        assign_perm("view_listviewpreference", preference.user, preference)
        assign_perm("change_listviewpreference", preference.user, preference)
        assign_perm("delete_listviewpreference", preference.user, preference)


def get_list_view_preference(
    user: User,
    organization: Organization,
    list_type: ListViewType,
) -> ListViewPreference:
    """

    Priority:
    1. User's personal preference (if exists)
    2. Organization default preference (if exists)
    3. Unsaved preference object with hardcoded defaults
    """
    return ListViewPreference.objects.get_for_user(user, organization, list_type)


def save_list_view_preference(  # noqa: PLR0913
    organization: Organization,
    list_type: ListViewType,
    *,
    user: User | None = None,
    visible_columns: list[str] | None = None,
    default_sort: str | None = None,
    saved_filters: dict[str, Any] | None = None,
    items_per_page: int | None = None,
) -> ListViewPreference:
    """
    Save or update a list preference.

    If user is provided, saves a user-level preference.
    If user is None, saves an organization-level default preference.
    """
    scope = PreferenceScope.USER if user else PreferenceScope.ORGANIZATION

    log_extra: dict[str, Any] = {
        "organization_id": organization.id,
        "list_type": list_type,
        "scope": scope.value,
    }
    if user:
        log_extra["user_id"] = user.id

    logger.info(
        "Saving list preference",
        extra=log_extra,
    )

    filter_kwargs: dict[str, Any] = {
        "organization": organization,
        "list_type": list_type,
        "scope": scope,
    }
    if user:
        filter_kwargs["user"] = user
    else:
        filter_kwargs["user__isnull"] = True

    pref, created = ListViewPreference.objects.update_or_create(
        **filter_kwargs,
        defaults={
            "visible_columns": visible_columns or [],
            "default_sort": default_sort or "",
            "saved_filters": saved_filters or {},
            "items_per_page": items_per_page or 25,
        },
    )

    if created:
        assign_default_listviewpreference_perms(pref)

    action = "created" if created else "updated"
    log_extra["preference_id"] = pref.id
    log_extra["action"] = action
    logger.info(
        "List preference %s",
        action,
        extra=log_extra,
    )

    return pref


def reset_list_view_preference(
    organization: Organization,
    list_type: ListViewType,
    *,
    user: User | None = None,
) -> None:
    """
    Reset a list preference, causing fallback to defaults.

    If user is provided, resets the user's personal preference (falls back to org or system defaults).
    If user is None, resets the organization's default preference (falls back to system defaults).
    """
    scope = PreferenceScope.USER if user else PreferenceScope.ORGANIZATION

    log_extra: dict[str, Any] = {
        "organization_id": organization.id,
        "list_type": list_type,
        "scope": scope.value,
    }
    if user:
        log_extra["user_id"] = user.id

    logger.info(
        "Resetting list preference",
        extra=log_extra,
    )

    filter_kwargs: dict[str, Any] = {
        "organization": organization,
        "list_type": list_type,
        "scope": scope,
    }
    if user:
        filter_kwargs["user"] = user
    else:
        filter_kwargs["user__isnull"] = True

    ListViewPreference.objects.filter(**filter_kwargs).delete()


def _get_custom_attribute_columns(
    list_type: ListViewType,
    organization: Organization,
) -> list[dict[str, str]]:
    """
    Get custom attribute columns for a list type within an organization.

    Custom attribute columns use the UUID as the value.
    """
    content_type = list_type.get_content_type()
    if not content_type:
        return []

    custom_attributes = CustomAttribute.objects.filter(
        organization=organization,
        content_type=content_type,
    ).order_by("name")

    columns = [
        {
            "value": str(attr.id),
            "label": attr.name,
            "data_type": attr.data_type,
            "is_custom": "true",
        }
        for attr in custom_attributes
    ]

    logger.debug(
        "Found custom attribute columns",
        extra={
            "list_type": list_type,
            "organization_id": organization.id,
            "count": len(columns),
        },
    )

    return columns


def get_available_columns(
    list_type: ListViewType,
    organization: Organization | None = None,
) -> list[dict[str, str]]:
    """
    Get all available columns for a list type with their labels.

    If organization is provided, includes custom attributes.
    """
    base_columns = list_type.get_column_definitions()

    # Add custom attribute columns if organization provided
    if organization:
        custom_columns = _get_custom_attribute_columns(list_type, organization)
        return base_columns + custom_columns

    return base_columns


def save_filters_to_preference(
    preference: ListViewPreference,
    filters: dict[str, Any],
) -> ListViewPreference:
    """
    Save filters to a ListViewPreference instance
    """
    organization = preference.organization
    list_type = ListViewType(preference.list_type)

    validate_and_clean_filters(filters, organization, list_type)
    return preference.save_filters(filters)


def _parse_filter_key(key: str) -> tuple[str, str | None]:
    remainder = key[len("filter_attr_") :]

    if remainder.endswith("_start"):
        return remainder[: -len("_start")], "start"
    if remainder.endswith("_end"):
        return remainder[: -len("_end")], "end"
    return remainder, None


def _parse_attribute_uuid(uuid_part: str) -> UUID | None:
    try:
        return UUID(uuid_part.replace("_", "-"))
    except (ValueError, AttributeError):
        return None


def _apply_range_filter(
    filters: dict[str, Any],
    attr_id_str: str,
    suffix: str,
    value: str | None,
) -> None:
    if attr_id_str not in filters["custom_attributes"]:
        filters["custom_attributes"][attr_id_str] = {}

    filters["custom_attributes"][attr_id_str]["operator"] = "range"
    filters["custom_attributes"][attr_id_str][suffix] = value


def _apply_values_filter(
    filters: dict[str, Any],
    attr_id_str: str,
    value: str,
) -> None:
    values = [v.strip() for v in value.split(",") if v.strip()]
    if values:
        if attr_id_str not in filters["custom_attributes"]:
            filters["custom_attributes"][attr_id_str] = {}
        filters["custom_attributes"][attr_id_str]["values"] = values


def _process_custom_attribute_filter(
    key: str,
    request: HttpRequest,
    filters: dict[str, Any],
) -> None:
    uuid_part, suffix = _parse_filter_key(key)
    attr_id = _parse_attribute_uuid(uuid_part)

    if attr_id is None:
        logger.warning(
            "Invalid attribute UUID in request filter",
            extra={"key": key, "uuid_part": uuid_part},
        )
        return

    attr_id_str = str(attr_id)
    value = request.GET.get(key)

    if suffix in ("start", "end"):
        _apply_range_filter(filters, attr_id_str, suffix, value)
    elif value:
        _apply_values_filter(filters, attr_id_str, value)


def parse_filters_from_request(
    request: HttpRequest,
    preference: ListViewPreference,
) -> dict[str, Any]:
    filters = preference.saved_filters.copy() if preference.saved_filters else {}

    if "custom_attributes" not in filters:
        filters["custom_attributes"] = {}
    if "model_fields" not in filters:
        filters["model_fields"] = {}

    for key in request.GET:
        if key.startswith("filter_attr_"):
            _process_custom_attribute_filter(key, request, filters)

    logger.debug(
        "Parsed filters from request",
        extra={
            "num_custom_filters": len(filters.get("custom_attributes", {})),
            "num_model_filters": len(filters.get("model_fields", {})),
            "has_request_overrides": any(key.startswith("filter_") for key in request.GET),
        },
    )

    return filters
