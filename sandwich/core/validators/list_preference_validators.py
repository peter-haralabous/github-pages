"""Validators for list view preferences and filters."""

import logging
from datetime import date
from typing import Any
from uuid import UUID

from django.contrib.contenttypes.models import ContentType

from sandwich.core.models import CustomAttribute
from sandwich.core.models import CustomAttributeEnum
from sandwich.core.models import ListViewType
from sandwich.core.models import Organization

logger = logging.getLogger(__name__)


def validate_list_type(
    list_type: str,
    *,
    user_id: int | None = None,
    organization_id: UUID | None = None,
) -> ListViewType:
    """
    Validate and convert string to ListViewType enum.
    """
    try:
        return ListViewType(list_type)
    except ValueError:
        log_extra: dict[str, Any] = {"list_type": list_type}
        if user_id:
            log_extra["user_id"] = user_id
        if organization_id:
            log_extra["organization_id"] = organization_id

        logger.warning(
            "Invalid list type",
            extra=log_extra,
        )
        raise


def validate_sort_field(
    sort_field: str,
    list_type: ListViewType,
    organization: Organization,
) -> bool:
    """
    Validate that a sort field is valid for the given list type and organization.
    """
    field = sort_field.lstrip("-")

    if field in list_type.get_standard_column_fields():
        return True

    try:
        attr_id = UUID(field)
        content_type = list_type.get_content_type()
        if content_type:
            return CustomAttribute.objects.filter(
                id=attr_id,
                organization=organization,
                content_type=content_type,
            ).exists()
    except (ValueError, AttributeError):
        pass

    return False


def _validate_enum_filter_values(
    attribute: CustomAttribute,
    filter_config: dict[str, Any],
) -> dict[str, str]:
    """Validate enum filter values against the attribute's allowed enum values."""
    errors = {}
    values = filter_config.get("values", [])

    if not isinstance(values, list):
        errors["values"] = "Enum filter values must be a list"
    elif values:
        valid_values = set(
            CustomAttributeEnum.objects.filter(attribute=attribute, value__in=values).values_list("value", flat=True)
        )
        invalid_values = [v for v in values if v not in valid_values]
        if invalid_values:
            errors["values"] = f"Invalid enum values: {', '.join(invalid_values)}"

    return errors


def _validate_date_value(value: Any, field_name: str = "value") -> dict[str, str]:
    """Validate a single date value, returning errors if invalid."""
    errors = {}
    if value:
        try:
            date.fromisoformat(value) if isinstance(value, str) else value
        except (ValueError, TypeError):
            errors[field_name] = f"Invalid date format for {field_name}"
    return errors


def _validate_date_range(start: Any, end: Any) -> dict[str, str]:
    """Validate date range values, checking format and logical ordering."""
    errors = {}

    if start:
        errors.update(_validate_date_value(start, "start"))

    if end:
        errors.update(_validate_date_value(end, "end"))

    if not errors and start and end:
        start_date = date.fromisoformat(start) if isinstance(start, str) else start
        end_date = date.fromisoformat(end) if isinstance(end, str) else end
        if start_date > end_date:
            errors["range"] = "Start date must be before or equal to end date"

    return errors


def _validate_date_filter(filter_config: dict[str, Any]) -> dict[str, str]:
    """Validate date filter configuration based on operator type."""
    errors = {}
    operator = filter_config.get("operator", "exact")

    if operator not in ("exact", "gte", "lte", "range"):
        errors["operator"] = f"Invalid date operator: {operator}"
        return errors

    if operator == "range":
        start = filter_config.get("start")
        end = filter_config.get("end")
        errors.update(_validate_date_range(start, end))
    else:
        value = filter_config.get("value")
        errors.update(_validate_date_value(value))

    return errors


def validate_custom_attribute_filter(
    attribute_id: UUID,
    filter_config: dict[str, Any],
    organization: Organization,
    content_type: ContentType,
) -> dict[str, str]:
    """
    Validate a custom attribute filter configuration.
    """
    errors = {}

    try:
        attribute = CustomAttribute.objects.get(id=attribute_id, organization=organization)
    except CustomAttribute.DoesNotExist:
        errors["attribute"] = f"Custom attribute {attribute_id} not found in organization"
        return errors

    if attribute.content_type_id != content_type.id:
        errors["content_type"] = (
            f"Attribute content_type ({attribute.content_type.model}) does not match expected ({content_type.model})"
        )
        return errors

    if attribute.data_type == CustomAttribute.DataType.ENUM:
        errors.update(_validate_enum_filter_values(attribute, filter_config))
    elif attribute.data_type == CustomAttribute.DataType.DATE:
        errors.update(_validate_date_filter(filter_config))

    logger.debug(
        "Validated custom attribute filter",
        extra={
            "attribute_id": str(attribute_id),
            "is_valid": len(errors) == 0,
            "errors": errors,
        },
    )

    return errors


def validate_and_clean_filters(
    filters: dict[str, Any],
    organization: Organization,
    list_type: ListViewType,
) -> None:
    """
    Validate custom attribute filters and remove invalid ones in-place.
    """
    content_type = list_type.get_content_type()
    if not content_type:
        return

    custom_attr_filters = filters.get("custom_attributes", {})
    invalid_keys = []

    for attr_id_str, filter_config in custom_attr_filters.items():
        try:
            attr_id = UUID(attr_id_str)
            errors = validate_custom_attribute_filter(attr_id, filter_config, organization, content_type)
            if errors:
                logger.warning(
                    "Invalid filter not saved",
                    extra={
                        "attribute_id": attr_id_str,
                        "errors": errors,
                    },
                )
                invalid_keys.append(attr_id_str)
        except (ValueError, AttributeError):
            logger.warning(
                "Invalid attribute UUID, removing filter",
                extra={"attribute_id_str": attr_id_str},
            )
            invalid_keys.append(attr_id_str)

    for key in invalid_keys:
        del filters["custom_attributes"][key]
