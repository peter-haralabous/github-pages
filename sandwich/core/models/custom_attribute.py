from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_enum import EnumField

from sandwich.core.models.abstract import BaseModel
from sandwich.core.models.organization import Organization


class CustomAttribute(BaseModel):
    """EAV Attribute model. Used to define custom attributes for various entities defined by the user."""

    class DataType(models.TextChoices):
        """Data type choices for custom attributes."""

        ENUM = "enum", _("Select")
        DATE = "date", _("Date")

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    data_type: models.Field[DataType, DataType] = EnumField(DataType)
    is_multi = models.BooleanField(
        default=False, help_text="Whether this attribute can have multiple values per entity."
    )


class CustomAttributeEnum(BaseModel):
    """Possible values for CustomAttribute of type ENUM."""

    attribute = models.ForeignKey(CustomAttribute, on_delete=models.CASCADE)
    label = models.CharField(max_length=255)
    value = models.SlugField(max_length=255)
    color_code = models.CharField(max_length=6, blank=True)  # e.g. "RRGGBB"

    class Meta:
        unique_together = ("attribute", "value")


class CustomAttributeValue(BaseModel):
    """Holds the value for a CustomAttribute for a given entity instance."""

    attribute = models.ForeignKey(CustomAttribute, on_delete=models.PROTECT)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = fields.GenericForeignKey("content_type", "object_id")

    # The value is stored in one of these fields depending on attribute.data_type
    value_date = models.DateField(null=True, blank=True)
    value_enum = models.ForeignKey(CustomAttributeEnum, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def _validate_attribute_ownership(self, errors: dict):
        """Validate that the attribute belongs to the same organization as the content object."""
        if hasattr(self.content_object, "organization_id") and self.content_object:
            if self.attribute.organization_id != self.content_object.organization_id:
                errors["attribute"] = ValidationError(
                    "Attribute organization must match content object's organization."
                )
        else:
            errors["content_object"] = ValidationError(
                f"Content object of type {self.content_type} has no organization_id field."
            )

    def _validate_content_type(self, errors: dict):
        """Validate that the attribute content type matches the value's content type."""
        if self.attribute.content_type_id != self.content_type_id:
            errors["content_type"] = ValidationError(
                "Attribute content_type must match the content_type of the value."
            )

    def _validate_value_type(self, errors: dict):
        """Validate that the correct value field is set based on the attribute's data type."""
        value_fields = {f.name for f in self._meta.get_fields() if f.name.startswith("value_")}

        # Map data types to valid field(s)
        data_type_field_map = {
            CustomAttribute.DataType.DATE: "value_date",
            CustomAttribute.DataType.ENUM: "value_enum",
        }

        allowed_fields = data_type_field_map.get(self.attribute.data_type)

        for field in value_fields:
            value = getattr(self, field)
            if field == allowed_fields:
                if value in (None, ""):
                    errors[field] = ValidationError(f"{field} must be set for {self.attribute.data_type} attributes.")
            elif value not in (None, ""):
                errors[field] = ValidationError(f"{field} must be null for {self.attribute.data_type} attributes.")

    def _validate_enum_value(self, errors: dict):
        """Validate that enum values belong to the correct attribute."""
        if self.attribute.data_type != CustomAttribute.DataType.ENUM or not self.value_enum:
            return
        if self.value_enum.attribute_id != self.attribute_id:
            errors["value_enum"] = ValidationError("value_enum must belong to the same attribute.")

    def _validate_multi_value_constraint(self, errors: dict):
        """Validate that single-value attributes don't have multiple values for the same object."""
        if self.attribute.is_multi:
            return
        existing = (
            CustomAttributeValue.objects.filter(
                attribute=self.attribute, content_type=self.content_type, object_id=self.object_id
            )
            .exclude(pk=self.pk)  # exclude self when updating
            .exists()
        )
        if existing:
            errors["attribute"] = ValidationError("Attribute cannot have multiple values for this object.")

    def clean(self):
        errors: dict[str, ValidationError] = {}

        self._validate_attribute_ownership(errors)
        self._validate_content_type(errors)
        self._validate_value_type(errors)
        self._validate_enum_value(errors)
        self._validate_multi_value_constraint(errors)

        if errors:
            raise ValidationError(errors)

        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
