"""Template tags for list view helpers."""

from typing import Any

from django import template

from sandwich.core.service.custom_attribute_query import _get_annotation_field_name
from sandwich.core.service.custom_attribute_query import _parse_custom_attribute_id

register = template.Library()


@register.filter
def get_attr(obj: Any, attr_name: str) -> Any:
    """
    Get a single attribute from an object.

    Used for accessing annotated custom attribute values.

    Example: {{ encounter|get_attr:"attr_550e8400_e29b_41d4_a716_446655440000" }}
    """
    try:
        return getattr(obj, attr_name, "")
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
def get_item(dictionary: dict, key: Any) -> Any:
    """
    Get an item from a dictionary by key.

    Used for accessing dictionary values in templates.

    Example: {{ my_dict|get_item:my_key }}
    """
    try:
        return dictionary.get(key)
    except (AttributeError, TypeError):
        return None
