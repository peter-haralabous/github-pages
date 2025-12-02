"""Template tags for list view helpers."""

from datetime import date
from typing import Any

from django import template
from django.contrib.contenttypes.models import ContentType

from sandwich.core.models import CustomAttribute
from sandwich.core.models import CustomAttributeValue
from sandwich.core.service.custom_attribute_query import _get_annotation_field_name
from sandwich.core.service.custom_attribute_query import _parse_custom_attribute_id
from sandwich.core.types import DATE_DISPLAY_FORMAT

register = template.Library()


@register.filter
def get_attr(obj: Any, attr_name: str) -> Any:
    """
    Get a single attribute from an object.

    Used for accessing annotated custom attribute values.

    For multi-select ENUM attributes, queries all values and joins with commas.
    For other attributes, uses the annotated value.

    Example: {{ encounter|get_attr:"attr_550e8400_e29b_41d4_a716_446655440000" }}
    """
    try:
        # First try to get the annotated value
        value = getattr(obj, attr_name, "")

        # Check if this is a custom attribute that might be multi-select
        attr_id = _parse_custom_attribute_id(attr_name.replace("attr_", "").replace("_", "-"))
        if attr_id:
            try:
                # Get the attribute to check if it's multi-select
                content_type = ContentType.objects.get_for_model(obj.__class__)
                attribute = CustomAttribute.objects.get(
                    id=attr_id,
                    content_type=content_type,
                    organization__isnull=False,  # Just to ensure we have an org
                )

                if attribute.data_type == CustomAttribute.DataType.ENUM and attribute.is_multi:
                    # For multi-select, query all values and join labels
                    attr_values = CustomAttributeValue.objects.filter(
                        attribute=attribute,
                        content_type=content_type,
                        object_id=obj.id,
                    ).select_related("value_enum")

                    labels = [av.value_enum.label for av in attr_values if av.value_enum]
                    return labels if labels else None
                if attribute.data_type == CustomAttribute.DataType.DATE:
                    # For date attributes, format consistently as YYYY-MM-DD
                    if isinstance(value, date):
                        return value.strftime(DATE_DISPLAY_FORMAT)
                    return value

            except (CustomAttribute.DoesNotExist, AttributeError):
                # Not a multi-select attribute or attribute not found, use annotated value
                pass
            else:
                return value
    except (AttributeError, TypeError):
        return ""


@register.filter
def custom_attr_name(column_value: str) -> str:
    """
    Convert a custom attribute UUID to its annotation field name.

    Example: {{ column.value|custom_attr_name }}
    """
    attr_id = _parse_custom_attribute_id(column_value)
    return _get_annotation_field_name(attr_id) if attr_id else ""


@register.filter
def is_list(column_value: str | list[str]) -> bool:
    """
    Determines whether or not column value is a string or a list of strings
    """
    return isinstance(column_value, list)
