import logging
from datetime import date
from typing import Any
from uuid import UUID

from django.contrib.contenttypes.models import ContentType
from django.db.models import Exists
from django.db.models import Model
from django.db.models import OuterRef
from django.db.models import Q
from django.db.models import QuerySet
from django.db.models import Subquery
from django.utils.dateparse import parse_date

from sandwich.core.models import CustomAttribute
from sandwich.core.models import CustomAttributeEnum
from sandwich.core.models import CustomAttributeValue
from sandwich.core.models import Organization

logger = logging.getLogger(__name__)


def _get_annotation_field_name(attribute_id: UUID) -> str:
    """Format a safe annotation field name for a custom attribute."""
    return f"attr_{str(attribute_id).replace('-', '_')}"


def _parse_custom_attribute_id(column_value: str) -> UUID | None:
    """
    Parse custom attribute ID from column value.

    Model field names (like 'patient__first_name') will fail UUID validation
    and return None.
    """
    try:
        return UUID(column_value)
    except (ValueError, AttributeError):
        # Not a UUID - this is a regular model field
        return None


def annotate_custom_attributes[ModelT: Model](
    queryset: QuerySet[ModelT],
    visible_columns: list[str],
    organization: Organization,
    content_type: ContentType,
) -> QuerySet[ModelT]:
    """
    Annotate queryset with custom attribute values for visible columns.

    Only annotates custom attributes in the visible_columns list.
    Uses subqueries to fetch values based on attribute data type.
    """
    custom_columns = [col for col in visible_columns if _parse_custom_attribute_id(col) is not None]

    if not custom_columns:
        logger.debug("No custom attributes to annotate")
        return queryset

    attributes = CustomAttribute.objects.filter(
        organization=organization,
        content_type=content_type,
    ).in_bulk()

    annotations = {}

    for column_value in custom_columns:
        attr_id = _parse_custom_attribute_id(column_value)
        if attr_id is None:
            continue

        attribute = attributes.get(attr_id)
        if not attribute:
            logger.warning(
                "Custom attribute not found, skipping annotation",
                extra={
                    "attribute_id": str(attr_id),
                    "organization_id": organization.id,
                },
            )
            continue

        annotation_name = _get_annotation_field_name(attr_id)

        if attribute.data_type == CustomAttribute.DataType.DATE:
            subquery = Subquery(
                CustomAttributeValue.objects.filter(
                    attribute_id=attr_id,
                    content_type=content_type,
                    object_id=OuterRef("pk"),
                ).values("value_date")[:1]
            )
        elif attribute.data_type == CustomAttribute.DataType.ENUM:
            subquery = Subquery(
                CustomAttributeValue.objects.filter(
                    attribute_id=attr_id,
                    content_type=content_type,
                    object_id=OuterRef("pk"),
                )
                .select_related("value_enum")
                .values("value_enum__label")[:1]
            )
        else:
            logger.warning(
                "Unsupported data type for custom attribute",
                extra={
                    "attribute_id": str(attr_id),
                    "data_type": attribute.data_type,
                },
            )
            continue

        annotations[annotation_name] = subquery
        logger.debug(
            "Added annotation for custom attribute",
            extra={
                "attribute_id": str(attr_id),
                "attribute_name": attribute.name,
                "annotation_name": annotation_name,
            },
        )

    if annotations:
        queryset = queryset.annotate(**annotations)
        logger.info(
            "Annotated queryset with custom attributes",
            extra={
                "organization_id": organization.id,
                "num_annotations": len(annotations),
            },
        )

    return queryset


def apply_sort_with_custom_attributes[ModelT: Model](
    queryset: QuerySet[ModelT],
    sort_field: str,
    organization: Organization,
    content_type: ContentType,
) -> QuerySet[ModelT]:
    """
    Apply sorting to queryset, handling custom attributes.

    If sort_field is a custom attribute, annotates the queryset and sorts by annotation.
    Otherwise, applies standard order_by.
    """
    if not sort_field:
        return queryset

    descending = sort_field.startswith("-")
    field_name = sort_field.lstrip("-")

    attr_id = _parse_custom_attribute_id(field_name)

    if attr_id:
        logger.debug(
            "Applying custom attribute sort",
            extra={
                "sort_field": sort_field,
                "attribute_id": str(attr_id),
            },
        )

        annotation_name = _get_annotation_field_name(attr_id)
        if annotation_name not in queryset.query.annotations:
            queryset = annotate_custom_attributes(
                queryset,
                [field_name],
                organization,
                content_type,
            )

        sort_by = f"-{annotation_name}" if descending else annotation_name
        queryset = queryset.order_by(sort_by)
    else:
        queryset = queryset.order_by(sort_field)

    return queryset


def _build_enum_filter(
    attribute: CustomAttribute,
    filter_config: dict[str, Any],
    content_type: ContentType,
) -> Q:
    """Build query filter for ENUM attributes"""
    values = filter_config.get("values", [])
    if not values:
        logger.debug("Empty enum filter values, returning no-op filter")
        return Q()

    include_null = filter_config.get("include_null", False)

    logger.debug(
        "Building enum filter with EXISTS pattern",
        extra={
            "attribute_id": str(attribute.id),
            "is_multi": attribute.is_multi,
            "values": values,
        },
    )

    filter_q = Q(
        Exists(
            CustomAttributeValue.objects.filter(
                attribute_id=attribute.id,
                content_type=content_type,
                object_id=OuterRef("pk"),
                value_enum__value__in=values,
            )
        )
    )

    if include_null:
        filter_q |= Q(
            ~Exists(
                CustomAttributeValue.objects.filter(
                    attribute_id=attribute.id,
                    content_type=content_type,
                    object_id=OuterRef("pk"),
                )
            )
        )

    return filter_q


def _build_date_exists_filter(
    attribute: CustomAttribute,
    content_type: ContentType,
    date_filters: dict[str, Any],
) -> Q:
    """Build EXISTS filter for date custom attribute with specified date filters."""
    return Q(
        Exists(
            CustomAttributeValue.objects.filter(
                attribute_id=attribute.id,
                content_type=content_type,
                object_id=OuterRef("pk"),
                **date_filters,
            )
        )
    )


def _build_date_filter_conditions(
    filter_config: dict[str, Any],
) -> tuple[str, dict[str, date]]:
    """Extract date filter conditions from config.

    Returns (operator, date_filters_dict) where date_filters_dict contains
    the normalized dates with their filter suffixes.
    """
    operator = filter_config.get("operator", "range")
    date_filters = {}

    operator_map = {
        "exact": ("", "value"),
        "gte": ("__gte", "value"),
        "lte": ("__lte", "value"),
    }

    if operator in operator_map:
        suffix, key = operator_map[operator]
        normalized_date = _normalize_date(filter_config.get(key))
        if normalized_date:
            date_filters[suffix] = normalized_date
    elif operator == "range":
        start_date = _normalize_date(filter_config.get("start"))
        end_date = _normalize_date(filter_config.get("end"))

        if start_date:
            date_filters["__gte"] = start_date
        if end_date:
            date_filters["__lte"] = end_date

    return operator, date_filters


def _build_date_filter_for_custom_attribute(
    attribute: CustomAttribute,
    filter_config: dict[str, Any],
    content_type: ContentType,
) -> Q:
    """Build Q filter for DATE custom attributes using EXISTS subquery.

    Uses EXISTS with date comparison in the subquery for better performance.
    """
    operator, date_filters = _build_date_filter_conditions(filter_config)
    include_null = filter_config.get("include_null", False)

    logger.debug(
        "Building date filter for custom attribute with EXISTS pattern",
        extra={
            "attribute_id": str(attribute.id),
            "operator": operator,
        },
    )

    filter_q = Q()

    if date_filters:
        # Convert suffixes to value_date field lookups
        value_date_filters = {f"value_date{suffix}": value for suffix, value in date_filters.items()}
        filter_q = _build_date_exists_filter(attribute, content_type, value_date_filters)

    if include_null:
        filter_q |= Q(
            ~Exists(
                CustomAttributeValue.objects.filter(
                    attribute_id=attribute.id,
                    content_type=content_type,
                    object_id=OuterRef("pk"),
                )
            )
        )

    return filter_q


def _normalize_date(date_value: str | date | None) -> date | None:
    """Convert string to date object if needed, return None if value is None."""
    if date_value is None:
        return None
    if isinstance(date_value, str):
        return date.fromisoformat(date_value)
    return date_value


def _build_date_filter(
    field_name: str,
    filter_config: dict[str, Any],
) -> Q:
    """Build Q filter for DATE model fields supporting exact, gte, lte, and range operators."""
    operator, date_filters = _build_date_filter_conditions(filter_config)
    include_null = filter_config.get("include_null", False)

    logger.debug(
        "Building date filter for model field",
        extra={
            "field_name": field_name,
            "operator": operator,
        },
    )

    filter_q = Q()

    if date_filters:
        # Build Q object with field lookups
        q_kwargs = {f"{field_name}{suffix}": value for suffix, value in date_filters.items()}
        filter_q = Q(**q_kwargs)

    if include_null:
        filter_q |= Q(**{f"{field_name}__isnull": True})

    return filter_q


def _build_enum_filter_for_field(
    field_name: str,
    filter_config: dict[str, Any],
) -> Q:
    """Build Q filter for ENUM model fields."""
    values = filter_config.get("values", [])
    if not values:
        logger.debug("Empty enum filter values, returning no-op filter")
        return Q()

    include_null = filter_config.get("include_null", False)

    logger.debug(
        "Building enum filter for model field",
        extra={
            "field_name": field_name,
            "values": values,
        },
    )

    filter_q = Q(**{f"{field_name}__in": values})

    if include_null:
        filter_q |= Q(**{f"{field_name}__isnull": True})

    return filter_q


def _build_filter_for_field(field_name: str, filter_config: dict[str, Any]) -> Q:
    """Build Q filter for a model field based on filter configuration."""
    filter_type = filter_config.get("type")

    if filter_type == "date" or "operator" in filter_config:
        return _build_date_filter(field_name, filter_config)
    if filter_type == "enum" or "values" in filter_config:
        return _build_enum_filter_for_field(field_name, filter_config)

    if "value" in filter_config:
        return Q(**{field_name: filter_config["value"]})

    logger.warning(
        "Unsupported filter configuration for model field",
        extra={"field_name": field_name, "filter_config": filter_config},
    )
    return Q()


def _build_custom_attribute_filter(
    attribute_id: UUID,
    filter_config: dict[str, Any],
    organization: Organization,
    content_type: ContentType,
) -> Q | None:
    """Build Q filter for a custom attribute, delegating to type-specific builders."""
    try:
        attribute = CustomAttribute.objects.select_related("organization").get(
            id=attribute_id, organization=organization, content_type=content_type
        )
    except CustomAttribute.DoesNotExist:
        logger.warning(
            "Custom attribute not found for filtering",
            extra={
                "attribute_id": str(attribute_id),
                "organization_id": organization.id,
                "content_type": content_type.model,
            },
        )
        return None

    logger.debug(
        "Building custom attribute filter",
        extra={
            "attribute_id": str(attribute_id),
            "attribute_name": attribute.name,
            "data_type": attribute.data_type,
        },
    )

    if attribute.data_type == CustomAttribute.DataType.ENUM:
        return _build_enum_filter(attribute, filter_config, content_type)
    if attribute.data_type == CustomAttribute.DataType.DATE:
        return _build_date_filter_for_custom_attribute(attribute, filter_config, content_type)
    logger.warning(
        "Unsupported data type for custom attribute filter",
        extra={
            "attribute_id": str(attribute_id),
            "data_type": attribute.data_type,
        },
    )
    return None


def _apply_custom_attribute_filters(
    queryset: QuerySet,
    custom_attr_filters: dict[str, Any],
    organization: Organization,
    content_type: ContentType,
) -> QuerySet:
    """Apply custom attribute filters to queryset."""
    combined_q = Q()
    for attr_id_str, filter_config in custom_attr_filters.items():
        attr_id = _parse_custom_attribute_id(attr_id_str)
        if not attr_id:
            logger.warning(
                "Invalid attribute UUID in filter",
                extra={"attribute_id_str": attr_id_str},
            )
            continue

        filter_q = _build_custom_attribute_filter(attr_id, filter_config, organization, content_type)
        if filter_q:
            combined_q &= filter_q

    if combined_q:
        queryset = queryset.filter(combined_q)
        logger.info(
            "Applied custom attribute filters",
            extra={
                "organization_id": organization.id,
                "num_filters": len(custom_attr_filters),
            },
        )

    return queryset


def _apply_model_field_filters(queryset: QuerySet, model_field_filters: dict[str, Any]) -> QuerySet:
    """Apply model field filters to the queryset"""
    combined_q = Q()

    for field, value in model_field_filters.items():
        actual_field = field.replace("_range", "") if field.endswith("_range") else field

        if isinstance(value, dict):
            filter_q = _build_filter_for_field(actual_field, value)
            if filter_q:
                combined_q &= filter_q
        elif isinstance(value, list):
            combined_q &= Q(**{f"{actual_field}__in": value})
        else:
            combined_q &= Q(**{actual_field: value})

    if combined_q:
        queryset = queryset.filter(combined_q)

    return queryset


def apply_filters_with_custom_attributes[ModelT: Model](
    queryset: QuerySet[ModelT],
    filters: dict[str, Any],
    organization: Organization,
    content_type: ContentType,
) -> QuerySet[ModelT]:
    """Apply filters to queryset, handling both model fields and custom attributes."""
    if not filters:
        logger.debug("No filters provided, returning unmodified queryset")
        return queryset

    custom_attr_filters = filters.get("custom_attributes", {})
    model_field_filters = filters.get("model_fields", {})

    logger.debug(
        "Applying filters",
        extra={
            "organization_id": organization.id,
            "num_custom_filters": len(custom_attr_filters),
            "num_model_filters": len(model_field_filters),
        },
    )

    if custom_attr_filters:
        queryset = _apply_custom_attribute_filters(queryset, custom_attr_filters, organization, content_type)

    if model_field_filters:
        queryset = _apply_model_field_filters(queryset, model_field_filters)
        logger.info(
            "Applied model field filters",
            extra={
                "organization_id": organization.id,
                "num_filters": len(model_field_filters),
            },
        )

    return queryset


def _update_multi_enum_attribute(
    encounter: Model,
    attribute: CustomAttribute,
    new_value: str | list[str],
    content_type: ContentType,
) -> bool:
    """Update a multi-valued ENUM custom attribute."""
    value_ids = ([new_value] if new_value else []) if isinstance(new_value, str) else new_value

    try:
        enum_values = list(CustomAttributeEnum.objects.filter(id__in=value_ids, attribute=attribute))
        if len(enum_values) != len(value_ids):
            logger.warning(
                "Some enum values not found for custom attribute update",
                extra={"attribute_id": str(attribute.id), "new_values": value_ids},
            )
            return False
    except (ValueError, CustomAttributeEnum.DoesNotExist):
        logger.warning(
            "Invalid enum values for custom attribute update",
            extra={"attribute_id": str(attribute.id), "new_values": value_ids},
        )
        return False

    # Delete existing values and then create new ones
    CustomAttributeValue.objects.filter(
        attribute=attribute,
        content_type=content_type,
        object_id=encounter.pk,
    ).delete()

    for enum_value in enum_values:
        CustomAttributeValue.objects.create(
            attribute=attribute,
            content_type=content_type,
            object_id=encounter.pk,
            value_enum=enum_value,
        )

    logger.info(
        "Updated multi-valued ENUM custom attribute",
        extra={
            "attribute_id": str(attribute.id),
            "encounter_id": encounter.pk,
            "enum_value_ids": [str(e.id) for e in enum_values],
        },
    )
    return True


def _update_single_enum_attribute(
    encounter: Model,
    attribute: CustomAttribute,
    new_value: str | list[str],
    content_type: ContentType,
) -> bool:
    """Update a single-valued ENUM custom attribute."""
    if isinstance(new_value, list):
        logger.warning(
            "Multiple values provided for single-value enum attribute",
            extra={"attribute_id": str(attribute.id), "new_values": new_value},
        )
        return False

    if not new_value or new_value.strip() == "":
        CustomAttributeValue.objects.filter(
            attribute=attribute,
            content_type=content_type,
            object_id=encounter.pk,
        ).delete()
        logger.info(
            "Cleared ENUM custom attribute",
            extra={
                "attribute_id": str(attribute.id),
                "encounter_id": encounter.pk,
            },
        )
        return True

    try:
        enum_value = CustomAttributeEnum.objects.get(id=new_value, attribute=attribute)
    except CustomAttributeEnum.DoesNotExist:
        logger.warning(
            "Invalid enum value for custom attribute update",
            extra={"attribute_id": str(attribute.id), "new_value": new_value},
        )
        return False

    CustomAttributeValue.objects.update_or_create(
        attribute=attribute,
        content_type=content_type,
        object_id=encounter.pk,
        defaults={"value_enum": enum_value},
    )
    logger.info(
        "Updated ENUM custom attribute",
        extra={
            "attribute_id": str(attribute.id),
            "encounter_id": encounter.pk,
            "enum_value_id": enum_value.id,
        },
    )
    return True


def _update_date_attribute(
    encounter: Model,
    attribute: CustomAttribute,
    new_value: str | list[str],
    content_type: ContentType,
) -> bool:
    """Update a DATE custom attribute."""
    if isinstance(new_value, list):
        logger.warning(
            "Multiple values provided for date attribute",
            extra={"attribute_id": str(attribute.id), "new_values": new_value},
        )
        return False

    if not new_value or new_value == "":
        CustomAttributeValue.objects.filter(
            attribute=attribute,
            content_type=content_type,
            object_id=encounter.pk,
        ).delete()
        logger.info(
            "Cleared DATE custom attribute",
            extra={
                "attribute_id": str(attribute.id),
                "encounter_id": encounter.pk,
            },
        )
        return True

    date_value = parse_date(new_value)
    if not date_value:
        logger.warning(
            "Invalid date value for custom attribute update",
            extra={"attribute_id": str(attribute.id), "new_value": new_value},
        )
        return False

    CustomAttributeValue.objects.update_or_create(
        attribute=attribute,
        content_type=content_type,
        object_id=encounter.pk,
        defaults={"value_date": date_value},
    )
    logger.info(
        "Updated DATE custom attribute",
        extra={
            "attribute_id": str(attribute.id),
            "encounter_id": encounter.pk,
            "date_value": date_value.isoformat(),
        },
    )
    return True


def update_custom_attribute(
    encounter: Model,
    attribute: CustomAttribute,
    new_value: str | list[str],
) -> bool:
    """Update a custom attribute value on the given model instance."""
    content_type = ContentType.objects.get_for_model(encounter.__class__)

    if attribute.data_type == CustomAttribute.DataType.ENUM:
        if attribute.is_multi:
            return _update_multi_enum_attribute(encounter, attribute, new_value, content_type)
        return _update_single_enum_attribute(encounter, attribute, new_value, content_type)

    if attribute.data_type == CustomAttribute.DataType.DATE:
        return _update_date_attribute(encounter, attribute, new_value, content_type)

    logger.warning(
        "Unsupported data type for custom attribute update",
        extra={"attribute_id": str(attribute.id), "data_type": attribute.data_type},
    )
    return False
