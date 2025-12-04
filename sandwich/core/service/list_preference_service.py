import copy
import logging
from collections.abc import Mapping
from collections.abc import Sequence
from typing import Any
from uuid import UUID

from django.http import HttpRequest
from guardian.shortcuts import assign_perm

from sandwich.core.models import CustomAttribute
from sandwich.core.models import CustomAttributeEnum
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


def _get_query_values(query_params: Mapping[str, Any], key: str) -> list[str]:
    if hasattr(query_params, "getlist"):
        values = query_params.getlist(key)
        return [str(value) for value in values if value is not None]

    value = query_params.get(key) if isinstance(query_params, Mapping) else None
    if value is None:
        return []

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [str(item) for item in value if item is not None]

    return [str(value)]


def _apply_range_filter(
    filters: dict[str, Any],
    attr_id_str: str,
    suffix: str,
    value: str | None,
) -> None:
    """Apply range filter for custom attributes."""
    if attr_id_str not in filters["custom_attributes"]:
        filters["custom_attributes"][attr_id_str] = {}

    filters["custom_attributes"][attr_id_str]["operator"] = "range"
    filters["custom_attributes"][attr_id_str][suffix] = value


def _parse_comma_separated_values(value: str) -> list[str]:
    """Parse comma-separated string into list of stripped values."""
    return [v.strip() for v in value.split(",") if v.strip()]


def _apply_values_filter(
    filters: dict[str, Any],
    attr_id_str: str,
    value: str,
) -> None:
    """Apply values filter for custom attributes."""
    values = _parse_comma_separated_values(value)
    if values:
        if attr_id_str not in filters["custom_attributes"]:
            filters["custom_attributes"][attr_id_str] = {}
        filters["custom_attributes"][attr_id_str]["values"] = values


def _process_custom_attribute_filter(
    key: str,
    query_params: Mapping[str, Any],
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
    values = _get_query_values(query_params, key)

    if suffix in ("start", "end"):
        value = values[-1] if values else None
        _apply_range_filter(filters, attr_id_str, suffix, value)
    elif values:
        joined_value = ",".join(values)
        _apply_values_filter(filters, attr_id_str, joined_value)


def _handle_range_suffix(
    key: str,
    field_name: str,
    query_params: Mapping[str, Any],
    filters: dict[str, Any],
) -> bool:
    """Handle range filter suffixes (_start and _end). Returns True if handled."""
    if field_name.endswith("_start"):
        base_field = field_name[: -len("_start")]
        range_filter = filters["model_fields"].setdefault(f"{base_field}_range", {"type": "date"})
        start_values = _get_query_values(query_params, key)
        if start_values:
            range_filter["start"] = start_values[-1]
        return True

    if field_name.endswith("_end"):
        base_field = field_name[: -len("_end")]
        range_filter = filters["model_fields"].setdefault(f"{base_field}_range", {"type": "date"})
        end_values = _get_query_values(query_params, key)
        if end_values:
            range_filter["end"] = end_values[-1]
        return True

    return False


def _handle_field_value(
    key: str,
    field_name: str,
    query_params: Mapping[str, Any],
    filters: dict[str, Any],
) -> None:
    """Handle regular field values."""
    values = _get_query_values(query_params, key)
    value = ",".join(values)
    if value:
        parsed_values = _parse_comma_separated_values(value)
        if len(parsed_values) > 1:
            filters["model_fields"][field_name] = parsed_values
        else:
            filters["model_fields"][field_name] = value


def _check_for_range_filters(
    key: str,
    field_name: str,
    query_params: Mapping[str, Any],
    filters: dict[str, Any],
) -> None:
    """Check for range filters (start/end suffixes) and add them."""
    start_key = f"{key}_start"
    end_key = f"{key}_end"
    start_values = _get_query_values(query_params, start_key)
    end_values = _get_query_values(query_params, end_key)
    if start_values or end_values:
        range_filter = {"type": "date"}
        if start_values:
            range_filter["start"] = start_values[-1]
        if end_values:
            range_filter["end"] = end_values[-1]
        if range_filter:
            filters["model_fields"][f"{field_name}_range"] = range_filter


def _process_model_field_filter(
    key: str,
    query_params: Mapping[str, Any],
    filters: dict[str, Any],
) -> None:
    """Process standard model field filters from URL params."""
    field_name = key[len("filter_") :]

    if _handle_range_suffix(key, field_name, query_params, filters):
        return

    _handle_field_value(key, field_name, query_params, filters)
    _check_for_range_filters(key, field_name, query_params, filters)


def _encode_model_field_to_params(field: str, value: Any, params: dict[str, str]) -> None:
    """Encode a single model field filter to URL parameters."""
    if isinstance(value, dict):
        base_field = field.replace("_range", "")
        start_val = value.get("start")
        end_val = value.get("end")
        if start_val:
            params[f"filter_{base_field}_start"] = str(start_val)
        if end_val:
            params[f"filter_{base_field}_end"] = str(end_val)
        if "values" in value:
            params[f"filter_{field}"] = ",".join(str(v) for v in value["values"])
    elif isinstance(value, list):
        params[f"filter_{field}"] = ",".join(str(v) for v in value)
    else:
        params[f"filter_{field}"] = str(value)


def _encode_custom_attribute_to_params(attr_id: str, filter_config: dict[str, Any], params: dict[str, str]) -> None:
    """Encode a single custom attribute filter to URL parameters."""
    attr_id_underscore = attr_id.replace("-", "_")
    if "values" in filter_config:
        params[f"filter_attr_{attr_id_underscore}"] = ",".join(filter_config["values"])
    elif "start" in filter_config or "end" in filter_config:
        if "start" in filter_config:
            params[f"filter_attr_{attr_id_underscore}_start"] = filter_config["start"]
        if "end" in filter_config:
            params[f"filter_attr_{attr_id_underscore}_end"] = filter_config["end"]


def encode_filters_to_url_params(filters: dict[str, Any]) -> dict[str, str]:
    """Encode filters dict to URL query parameters."""
    params: dict[str, str] = {}

    for field, value in filters.get("model_fields", {}).items():
        _encode_model_field_to_params(field, value, params)

    for attr_id, filter_config in filters.get("custom_attributes", {}).items():
        _encode_custom_attribute_to_params(attr_id, filter_config, params)

    return params


def has_unsaved_filters(request: HttpRequest, preference: ListViewPreference) -> bool:
    """Check if current URL filters differ from saved preference filters."""
    # If in custom filter mode, always show as unsaved
    filter_mode = request.GET.get("filter_mode")
    if filter_mode == "custom":
        return True

    saved_params = encode_filters_to_url_params(preference.saved_filters or {})
    current_params = {
        key: ",".join(_get_query_values(request.GET, key)) for key in request.GET if key.startswith("filter_")
    }

    return current_params != saved_params


def _normalize_range_filter(field_name: str, filter_value: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Normalize a range filter to consistent format."""
    base_field_name = field_name[: -len("_range")] if field_name.endswith("_range") else field_name
    return base_field_name, {
        "type": "date",
        "operator": "range",
        "start": filter_value.get("start"),
        "end": filter_value.get("end"),
    }


def _enrich_enum_filter(
    filter_value: list[str],
    choices_dict: dict[str, str],
) -> dict[str, Any]:
    """Enrich enum filter with display values."""
    return {
        "values": filter_value,
        "display_values": [choices_dict.get(val, val) for val in filter_value],
        "type": "enum",
    }


def _enrich_custom_attribute_filter(
    attr_id_str: str,
    filter_config: dict[str, Any],
    organization: Organization,
) -> dict[str, Any]:
    """Enrich a single custom attribute filter with type and display values."""
    try:
        attr_uuid = UUID(attr_id_str)
        attribute = CustomAttribute.objects.get(
            id=attr_uuid,
            organization=organization,
        )

        if "type" not in filter_config:
            filter_config["type"] = attribute.data_type

        if filter_config.get("type") == "enum" and "values" in filter_config:
            enum_values = CustomAttributeEnum.objects.filter(attribute=attribute).in_bulk(field_name="value")
            choices_dict = {ev.value: ev.label for ev in enum_values.values()}
            return {**filter_config, **_enrich_enum_filter(filter_config["values"], choices_dict)}

    except (ValueError, CustomAttribute.DoesNotExist):
        logger.warning(
            "Could not enrich custom attribute filter",
            extra={"attr_id": attr_id_str},
        )
        if "values" in filter_config:
            filter_config["display_values"] = filter_config["values"]

    return filter_config


def _enrich_model_field_filter(
    field_name: str,
    filter_value: Any,
    list_type: ListViewType | None,
) -> tuple[str, Any]:
    """Enrich a single model field filter with display values."""
    if field_name.endswith("_range") and isinstance(filter_value, dict):
        return _normalize_range_filter(field_name, filter_value)

    if isinstance(filter_value, list) and list_type:
        field_type = list_type.get_field_type(field_name)
        if field_type == "enum":
            choices_dict = dict(list_type.get_field_choices(field_name))
            return field_name, _enrich_enum_filter(filter_value, choices_dict)

    return field_name, filter_value


def enrich_filters_with_display_values(
    filters: dict[str, Any],
    organization: Organization,
    list_type: ListViewType | None = None,
) -> dict[str, Any]:
    """Enrich filter configuration with display-friendly values."""
    enriched = copy.deepcopy(filters)

    enriched["custom_attributes"] = {
        attr_id_str: _enrich_custom_attribute_filter(attr_id_str, filter_config, organization)
        for attr_id_str, filter_config in enriched.get("custom_attributes", {}).items()
    }

    enriched["model_fields"] = dict(
        _enrich_model_field_filter(field_name, filter_value, list_type)
        for field_name, filter_value in enriched.get("model_fields", {}).items()
    )

    return enriched


def parse_filters_from_query_params(query_params: Mapping[str, Any]) -> dict[str, Any]:
    filters: dict[str, Any] = {"custom_attributes": {}, "model_fields": {}}

    keys = query_params.keys() if hasattr(query_params, "keys") else []
    for key in keys:
        if key == "filter_mode":
            continue
        if key.startswith("filter_attr_"):
            _process_custom_attribute_filter(key, query_params, filters)
        elif key.startswith("filter_") and key != "filter_attr_":
            _process_model_field_filter(key, query_params, filters)

    logger.debug(
        "Parsed filters from query params",
        extra={
            "num_custom_filters": len(filters.get("custom_attributes", {})),
            "num_model_filters": len(filters.get("model_fields", {})),
            "has_query_filters": any(key.startswith("filter_") for key in keys),
        },
    )

    return filters
