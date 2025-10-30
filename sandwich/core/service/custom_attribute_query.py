import logging
from uuid import UUID

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from django.db.models import OuterRef
from django.db.models import QuerySet
from django.db.models import Subquery

from sandwich.core.models import CustomAttribute
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
