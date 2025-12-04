"""Tests for list preference validators."""

from uuid import uuid4

import pytest
from django.contrib.contenttypes.models import ContentType

from sandwich.core.factories.organization import OrganizationFactory
from sandwich.core.models import CustomAttribute
from sandwich.core.models import CustomAttributeEnum
from sandwich.core.models import ListViewType
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.patient import Patient
from sandwich.core.validators.list_preference_validators import validate_and_clean_filters
from sandwich.core.validators.list_preference_validators import validate_custom_attribute_filter
from sandwich.core.validators.list_preference_validators import validate_list_type
from sandwich.core.validators.list_preference_validators import validate_sort_field


@pytest.mark.django_db
class TestValidateListType:
    """Test validate_list_type function."""

    def test_valid_list_type(self):
        """Valid list type string should convert to enum."""
        result = validate_list_type("encounter_list")
        assert result == ListViewType.ENCOUNTER_LIST

    def test_invalid_list_type_raises_error(self):
        """Invalid list type string should raise ValueError."""
        with pytest.raises(ValueError, match="'invalid_type' is not a valid ListViewType"):
            validate_list_type("invalid_type")


@pytest.mark.django_db
class TestValidateSortField:
    """Test validate_sort_field function."""

    def test_valid_standard_field(self):
        """Standard field should be valid."""
        org = OrganizationFactory.create()
        assert validate_sort_field("first_name", ListViewType.PATIENT_LIST, org)

    def test_valid_descending_field(self):
        """Field with leading '-' should be valid."""
        org = OrganizationFactory.create()
        assert validate_sort_field("-updated_at", ListViewType.PATIENT_LIST, org)

    def test_invalid_field(self):
        """Non-existent field should be invalid."""
        org = OrganizationFactory.create()
        assert not validate_sort_field("nonexistent_field", ListViewType.PATIENT_LIST, org)

    def test_valid_custom_attribute_field(self):
        """Custom attribute UUID should be valid sort field."""
        org = OrganizationFactory.create()
        content_type = ContentType.objects.get_for_model(Patient)
        attr = CustomAttribute.objects.create(
            organization=org,
            content_type=content_type,
            name="Test Attribute",
            data_type=CustomAttribute.DataType.DATE,
        )
        assert validate_sort_field(str(attr.id), ListViewType.PATIENT_LIST, org)


@pytest.mark.django_db
class TestValidateCustomAttributeFilter:
    """Test validate_custom_attribute_filter function."""

    def test_valid_enum_filter(self):
        """Valid enum filter should pass validation."""
        org = OrganizationFactory.create()
        content_type = ContentType.objects.get_for_model(Patient)
        attr = CustomAttribute.objects.create(
            organization=org,
            content_type=content_type,
            name="Status",
            data_type=CustomAttribute.DataType.ENUM,
        )
        CustomAttributeEnum.objects.create(attribute=attr, value="active")
        CustomAttributeEnum.objects.create(attribute=attr, value="inactive")

        errors = validate_custom_attribute_filter(
            attr.id,
            {"values": ["active", "inactive"]},
            org,
            content_type,
        )
        assert len(errors) == 0

    def test_invalid_enum_values(self):
        """Invalid enum values should return errors."""
        org = OrganizationFactory.create()
        content_type = ContentType.objects.get_for_model(Patient)
        attr = CustomAttribute.objects.create(
            organization=org,
            content_type=content_type,
            name="Status",
            data_type=CustomAttribute.DataType.ENUM,
        )
        CustomAttributeEnum.objects.create(attribute=attr, value="active")

        errors = validate_custom_attribute_filter(
            attr.id,
            {"values": ["active", "invalid_value"]},
            org,
            content_type,
        )
        assert "values" in errors
        assert "invalid_value" in errors["values"]

    def test_valid_date_range_filter(self):
        """Valid date range filter should pass validation."""
        org = OrganizationFactory.create()
        content_type = ContentType.objects.get_for_model(Patient)
        attr = CustomAttribute.objects.create(
            organization=org,
            content_type=content_type,
            name="Appointment Date",
            data_type=CustomAttribute.DataType.DATE,
        )

        errors = validate_custom_attribute_filter(
            attr.id,
            {"operator": "range", "start": "2024-01-01", "end": "2024-12-31"},
            org,
            content_type,
        )
        assert len(errors) == 0

    def test_invalid_date_range(self):
        """Date range with start after end should return error."""
        org = OrganizationFactory.create()
        content_type = ContentType.objects.get_for_model(Patient)
        attr = CustomAttribute.objects.create(
            organization=org,
            content_type=content_type,
            name="Appointment Date",
            data_type=CustomAttribute.DataType.DATE,
        )

        errors = validate_custom_attribute_filter(
            attr.id,
            {"operator": "range", "start": "2024-12-31", "end": "2024-01-01"},
            org,
            content_type,
        )
        assert "range" in errors

    def test_nonexistent_attribute(self):
        """Non-existent attribute should return error."""
        org = OrganizationFactory.create()
        content_type = ContentType.objects.get_for_model(Patient)

        errors = validate_custom_attribute_filter(
            uuid4(),
            {"values": ["test"]},
            org,
            content_type,
        )
        assert "attribute" in errors

    def test_wrong_content_type(self):
        """Attribute with wrong content type should return error."""
        org = OrganizationFactory.create()
        patient_ct = ContentType.objects.get_for_model(Patient)
        encounter_ct = ContentType.objects.get_for_model(Encounter)

        attr = CustomAttribute.objects.create(
            organization=org,
            content_type=patient_ct,
            name="Test",
            data_type=CustomAttribute.DataType.DATE,
        )

        errors = validate_custom_attribute_filter(
            attr.id,
            {"operator": "exact", "value": "2024-01-01"},
            org,
            encounter_ct,
        )
        assert "content_type" in errors


@pytest.mark.django_db
class TestValidateAndCleanFilters:
    """Test validate_and_clean_filters function."""

    def test_removes_invalid_filters(self):
        """Invalid filters should be removed from dict."""
        org = OrganizationFactory.create()
        filters = {
            "custom_attributes": {
                str(uuid4()): {"values": ["test"]},  # Non-existent attribute
            }
        }

        validate_and_clean_filters(filters, org, ListViewType.PATIENT_LIST)
        assert len(filters["custom_attributes"]) == 0

    def test_keeps_valid_filters(self):
        """Valid filters should be kept."""
        org = OrganizationFactory.create()
        content_type = ContentType.objects.get_for_model(Patient)
        attr = CustomAttribute.objects.create(
            organization=org,
            content_type=content_type,
            name="Status",
            data_type=CustomAttribute.DataType.ENUM,
        )
        CustomAttributeEnum.objects.create(attribute=attr, value="active")

        filters = {
            "custom_attributes": {
                str(attr.id): {"values": ["active"]},
            }
        }

        validate_and_clean_filters(filters, org, ListViewType.PATIENT_LIST)
        assert str(attr.id) in filters["custom_attributes"]
