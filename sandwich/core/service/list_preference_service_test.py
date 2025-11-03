"""Unit tests for list preference model and service."""

from uuid import uuid4

import pytest
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.test import RequestFactory

from sandwich.core.factories.organization import OrganizationFactory
from sandwich.core.models import CustomAttribute
from sandwich.core.models import CustomAttributeEnum
from sandwich.core.models import ListViewPreference
from sandwich.core.models import ListViewType
from sandwich.core.models import PreferenceScope
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.patient import Patient
from sandwich.core.service.list_preference_service import _get_custom_attribute_columns
from sandwich.core.service.list_preference_service import get_available_columns
from sandwich.core.service.list_preference_service import get_list_view_preference
from sandwich.core.service.list_preference_service import parse_filters_from_request
from sandwich.core.service.list_preference_service import reset_list_view_preference
from sandwich.core.service.list_preference_service import save_filters_to_preference
from sandwich.core.service.list_preference_service import save_list_view_preference
from sandwich.core.validators.list_preference_validators import validate_custom_attribute_filter
from sandwich.core.validators.list_preference_validators import validate_sort_field


@pytest.mark.django_db
class TestListViewPreferenceModel:
    """Test the ListViewPreference model constraints and behavior."""

    def test_create_user_preference(self, user, organization):
        """User can create a preference for a list type."""
        pref = ListViewPreference.objects.create(
            user=user,
            organization=organization,
            list_type=ListViewType.ENCOUNTER_LIST,
            scope=PreferenceScope.USER,
            visible_columns=["patient__first_name", "patient__email"],
            default_sort="-updated_at",
            items_per_page=50,
        )

        assert pref.user == user
        assert pref.organization == organization
        assert pref.list_type == ListViewType.ENCOUNTER_LIST
        assert pref.scope == PreferenceScope.USER
        assert len(pref.visible_columns) == 2
        assert pref.items_per_page == 50

    def test_user_preference_unique_constraint(self, user, organization):
        """User can only have one preference per list type in an organization."""

        ListViewPreference.objects.create(
            user=user,
            organization=organization,
            list_type=ListViewType.ENCOUNTER_LIST,
            scope=PreferenceScope.USER,
        )

        with pytest.raises(IntegrityError):
            ListViewPreference.objects.create(
                user=user,
                organization=organization,
                list_type=ListViewType.ENCOUNTER_LIST,
                scope=PreferenceScope.USER,
            )

    def test_org_preference_unique_constraint(self, organization):
        """Organization can only have one default preference per list type."""

        ListViewPreference.objects.create(
            organization=organization,
            list_type=ListViewType.ENCOUNTER_LIST,
            scope=PreferenceScope.ORGANIZATION,
            user=None,
        )

        with pytest.raises(IntegrityError):
            ListViewPreference.objects.create(
                organization=organization,
                list_type=ListViewType.ENCOUNTER_LIST,
                scope=PreferenceScope.ORGANIZATION,
                user=None,
            )

    def test_user_can_have_different_preferences_for_different_lists(self, user, organization):
        """User can have different preferences for encounter_list and patient_list."""

        encounter_pref = ListViewPreference.objects.create(
            user=user,
            organization=organization,
            list_type=ListViewType.ENCOUNTER_LIST,
            scope=PreferenceScope.USER,
            visible_columns=["patient__first_name"],
        )

        patient_pref = ListViewPreference.objects.create(
            user=user,
            organization=organization,
            list_type=ListViewType.PATIENT_LIST,
            scope=PreferenceScope.USER,
            visible_columns=["first_name", "email"],
        )

        assert encounter_pref.id != patient_pref.id
        assert encounter_pref.visible_columns != patient_pref.visible_columns

    def test_scope_user_consistency_constraint(self, organization):
        """User-scoped preference must have a user, org-scoped must not."""

        # This should fail - USER scope without user
        with pytest.raises(IntegrityError):
            ListViewPreference.objects.create(
                organization=organization,
                list_type=ListViewType.ENCOUNTER_LIST,
                scope=PreferenceScope.USER,
                user=None,
            )

    def test_str_representation(self, user, organization):
        """Test __str__ method for both scopes."""

        user_pref = ListViewPreference.objects.create(
            user=user,
            organization=organization,
            list_type=ListViewType.ENCOUNTER_LIST,
            scope=PreferenceScope.USER,
        )
        assert str(user) in str(user_pref)
        assert ListViewType.ENCOUNTER_LIST.value in str(user_pref)

        org_pref = ListViewPreference.objects.create(
            organization=organization,
            list_type=ListViewType.PATIENT_LIST,
            scope=PreferenceScope.ORGANIZATION,
            user=None,
        )
        assert str(organization) in str(org_pref)
        assert "org default" in str(org_pref)


@pytest.mark.django_db
class TestListPreferenceService:
    """Test the list preference service functions."""

    def test_get_preference_returns_defaults_when_no_preferences_exist(self, user, organization):
        """When no preferences exist, return unsaved preference with hardcoded defaults."""
        ListViewPreference.objects.filter(organization=organization).delete()

        pref = get_list_view_preference(user, organization, ListViewType.ENCOUNTER_LIST)

        assert pref is not None
        assert pref.visible_columns == ListViewPreference.get_default_columns(ListViewType.ENCOUNTER_LIST)
        assert pref.default_sort == ListViewPreference.get_default_sort(ListViewType.ENCOUNTER_LIST)
        assert pref.items_per_page == 25

    def test_get_preference_returns_user_preference_when_exists(self, user, organization):
        """User preference is returned when it exists."""

        user_pref = save_list_view_preference(
            organization=organization,
            list_type=ListViewType.ENCOUNTER_LIST,
            user=user,
            visible_columns=["patient__first_name"],
        )

        pref = get_list_view_preference(user, organization, ListViewType.ENCOUNTER_LIST)

        assert pref is not None
        assert pref.id == user_pref.id
        assert pref.scope == PreferenceScope.USER

    def test_preference_inheritance(self, user, organization):
        """User preferences override organization defaults."""

        # Create org default
        org_pref = save_list_view_preference(
            organization=organization,
            list_type=ListViewType.ENCOUNTER_LIST,
            visible_columns=["patient__first_name", "patient__email"],
            items_per_page=10,
        )

        # User should get org default
        pref = get_list_view_preference(user, organization, ListViewType.ENCOUNTER_LIST)
        assert pref is not None
        assert pref.id == org_pref.id
        assert pref.items_per_page == 10

        # Create user preference
        user_pref = save_list_view_preference(
            organization=organization,
            list_type=ListViewType.ENCOUNTER_LIST,
            user=user,
            visible_columns=["patient__first_name"],
            items_per_page=50,
        )

        # User should now get their own preference
        pref = get_list_view_preference(user, organization, ListViewType.ENCOUNTER_LIST)
        assert pref is not None
        assert pref.id == user_pref.id
        assert pref.items_per_page == 50

    def test_save_user_preference_creates_new_preference(self, user, organization):
        """save_list_view_preference creates a new user preference."""

        pref = save_list_view_preference(
            organization=organization,
            list_type=ListViewType.ENCOUNTER_LIST,
            user=user,
            visible_columns=["patient__first_name", "patient__email"],
            default_sort="-created_at",
            items_per_page=100,
        )

        assert pref.user == user
        assert pref.organization == organization
        assert len(pref.visible_columns) == 2
        assert pref.default_sort == "-created_at"
        assert pref.items_per_page == 100

    def test_save_user_preference_updates_existing(self, user, organization):
        """save_list_view_preference updates existing user preference."""

        # Create initial preference
        pref1 = save_list_view_preference(
            organization=organization,
            list_type=ListViewType.ENCOUNTER_LIST,
            user=user,
            visible_columns=["patient__first_name"],
            items_per_page=25,
        )

        # Update it
        pref2 = save_list_view_preference(
            organization=organization,
            list_type=ListViewType.ENCOUNTER_LIST,
            user=user,
            visible_columns=["patient__first_name", "patient__email", "created_at"],
            items_per_page=50,
        )

        # Should be the same object, updated
        assert pref1.id == pref2.id
        assert len(pref2.visible_columns) == 3
        assert pref2.items_per_page == 50

        # Should only be one preference in DB
        count = ListViewPreference.objects.filter(
            user=user, organization=organization, list_type=ListViewType.ENCOUNTER_LIST
        ).count()
        assert count == 1

    def test_save_organization_default(self, organization):
        """save_list_view_preference creates org preference."""

        pref = save_list_view_preference(
            organization=organization,
            list_type=ListViewType.ENCOUNTER_LIST,
            visible_columns=["patient__first_name", "patient__email"],
            default_sort="-updated_at",
        )

        assert pref.organization == organization
        assert pref.user is None
        assert pref.scope == PreferenceScope.ORGANIZATION
        assert len(pref.visible_columns) == 2

    def test_reset_user_preference(self, user, organization):
        """reset_list_view_preference deletes user preference causing fallback."""

        # Create user preference
        save_list_view_preference(
            organization=organization,
            list_type=ListViewType.ENCOUNTER_LIST,
            user=user,
            visible_columns=["patient__first_name"],
        )

        # Create org default
        org_pref = save_list_view_preference(
            organization=organization,
            list_type=ListViewType.ENCOUNTER_LIST,
            visible_columns=["patient__first_name", "patient__email"],
        )

        # User should get their preference
        pref = get_list_view_preference(user, organization, ListViewType.ENCOUNTER_LIST)
        assert pref is not None
        assert pref.scope == PreferenceScope.USER

        # Reset user preference
        reset_list_view_preference(organization=organization, list_type=ListViewType.ENCOUNTER_LIST, user=user)

        # User should now get org default
        pref = get_list_view_preference(user, organization, ListViewType.ENCOUNTER_LIST)
        assert pref is not None
        assert pref.id == org_pref.id
        assert pref.scope == PreferenceScope.ORGANIZATION

    def test_get_default_columns(self):
        """get_default_columns returns correct defaults for each list type."""
        encounter_cols = ListViewPreference.get_default_columns(ListViewType.ENCOUNTER_LIST)
        assert "patient__first_name" in encounter_cols
        assert "patient__email" in encounter_cols
        assert len(encounter_cols) > 0

        patient_cols = ListViewPreference.get_default_columns(ListViewType.PATIENT_LIST)
        assert "first_name" in patient_cols
        assert "email" in patient_cols
        assert len(patient_cols) > 0

    def test_get_default_sort(self):
        """get_default_sort returns correct defaults for each list type."""
        encounter_sort = ListViewPreference.get_default_sort(ListViewType.ENCOUNTER_LIST)
        assert encounter_sort == "-updated_at"

        patient_sort = ListViewPreference.get_default_sort(ListViewType.PATIENT_LIST)
        assert patient_sort == "-updated_at"

    def test_get_available_columns(self):
        """get_available_columns returns all available columns with labels."""
        encounter_cols = get_available_columns(ListViewType.ENCOUNTER_LIST)
        assert len(encounter_cols) > 0
        assert all("value" in col and "label" in col for col in encounter_cols)

        patient_cols = get_available_columns(ListViewType.PATIENT_LIST)
        assert len(patient_cols) > 0
        assert all("value" in col and "label" in col for col in patient_cols)

    def test_inactive_preferences_not_returned(self, user, organization):
        """Deleted (previously inactive) preferences fall back to defaults."""
        ListViewPreference.objects.filter(organization=organization).delete()

        # Simulate previously inactive preference by creating then deleting
        temp_pref = ListViewPreference.objects.create(
            user=user,
            organization=organization,
            list_type=ListViewType.ENCOUNTER_LIST,
            scope=PreferenceScope.USER,
        )
        temp_pref.delete()

        pref = get_list_view_preference(user, organization, ListViewType.ENCOUNTER_LIST)
        assert pref is not None
        # Preference falls back to defaults regardless of persistence state
        assert pref.visible_columns == ListViewPreference.get_default_columns(ListViewType.ENCOUNTER_LIST)

    def test_different_orgs_have_separate_preferences(self, user):
        """User preferences are scoped per organization."""
        org1 = OrganizationFactory.create()
        org2 = OrganizationFactory.create()

        # Create preference for org1
        pref1 = save_list_view_preference(
            organization=org1,
            list_type=ListViewType.ENCOUNTER_LIST,
            user=user,
            visible_columns=["patient__first_name"],
        )

        # Create preference for org2
        pref2 = save_list_view_preference(
            organization=org2,
            list_type=ListViewType.ENCOUNTER_LIST,
            user=user,
            visible_columns=["patient__first_name", "patient__email"],
        )

        # Different preferences for different orgs
        assert pref1.id != pref2.id
        assert len(pref1.visible_columns) != len(pref2.visible_columns)


@pytest.mark.django_db
class TestCustomAttributeColumns:
    def test_get_custom_attribute_columns_for_encounter(self, organization):
        content_type = ContentType.objects.get_for_model(Encounter)

        attr1 = CustomAttribute.objects.create(
            organization=organization,
            content_type=content_type,
            name="Priority",
            data_type=CustomAttribute.DataType.ENUM,
        )
        attr2 = CustomAttribute.objects.create(
            organization=organization,
            content_type=content_type,
            name="Follow-up Date",
            data_type=CustomAttribute.DataType.DATE,
        )

        columns = _get_custom_attribute_columns(ListViewType.ENCOUNTER_LIST, organization)

        assert len(columns) == 2
        # Find columns by ID since order is alphabetical by name
        column_values = {col["value"] for col in columns}
        assert str(attr1.id) in column_values
        assert str(attr2.id) in column_values

        # Verify all columns have required fields
        for col in columns:
            assert "value" in col
            assert "label" in col
            assert "data_type" in col
            assert col["is_custom"] == "true"

        # Verify labels are correct
        labels = {col["label"] for col in columns}
        assert "Priority" in labels
        assert "Follow-up Date" in labels

    def test_get_available_columns_includes_custom_attributes_when_org_provided(self, organization):
        content_type = ContentType.objects.get_for_model(Encounter)

        CustomAttribute.objects.create(
            organization=organization,
            content_type=content_type,
            name="Custom Field",
            data_type=CustomAttribute.DataType.ENUM,
        )

        # Without organization
        columns_without_org = get_available_columns(ListViewType.ENCOUNTER_LIST)
        assert all(not col.get("is_custom") for col in columns_without_org)

        # With organization
        columns_with_org = get_available_columns(ListViewType.ENCOUNTER_LIST, organization)
        assert len(columns_with_org) > len(columns_without_org)
        custom_cols = [col for col in columns_with_org if col.get("is_custom")]
        assert len(custom_cols) == 1
        assert custom_cols[0]["label"] == "Custom Field"

    def test_custom_attributes_filtered_by_content_type(self, organization):
        encounter_ct = ContentType.objects.get_for_model(Encounter)
        patient_ct = ContentType.objects.get_for_model(Patient)

        # Create attribute for encounters
        CustomAttribute.objects.create(
            organization=organization,
            content_type=encounter_ct,
            name="Encounter Field",
            data_type=CustomAttribute.DataType.ENUM,
        )

        # Create attribute for patients
        CustomAttribute.objects.create(
            organization=organization,
            content_type=patient_ct,
            name="Patient Field",
            data_type=CustomAttribute.DataType.ENUM,
        )

        encounter_columns = _get_custom_attribute_columns(ListViewType.ENCOUNTER_LIST, organization)
        patient_columns = _get_custom_attribute_columns(ListViewType.PATIENT_LIST, organization)

        assert len(encounter_columns) == 1
        assert encounter_columns[0]["label"] == "Encounter Field"
        assert len(patient_columns) == 1
        assert patient_columns[0]["label"] == "Patient Field"

    def test_validate_sort_field_accepts_custom_attributes(self, organization):
        content_type = ContentType.objects.get_for_model(Encounter)

        attr = CustomAttribute.objects.create(
            organization=organization,
            content_type=content_type,
            name="Priority",
            data_type=CustomAttribute.DataType.ENUM,
        )

        assert validate_sort_field(str(attr.id), ListViewType.ENCOUNTER_LIST, organization)
        assert validate_sort_field(f"-{attr.id}", ListViewType.ENCOUNTER_LIST, organization)
        assert validate_sort_field("patient__first_name", ListViewType.ENCOUNTER_LIST, organization)
        assert not validate_sort_field("nonexistent_field", ListViewType.ENCOUNTER_LIST, organization)


@pytest.mark.django_db
class TestFilterValidation:
    """Test custom attribute filter validation."""

    def test_validate_enum_filter_valid_values(self, organization):
        content_type = ContentType.objects.get_for_model(Encounter)

        attr = CustomAttribute.objects.create(
            organization=organization,
            content_type=content_type,
            name="Priority",
            data_type=CustomAttribute.DataType.ENUM,
        )
        CustomAttributeEnum.objects.create(attribute=attr, label="High", value="high")
        CustomAttributeEnum.objects.create(attribute=attr, label="Low", value="low")

        filter_config = {"type": "enum", "values": ["high", "low"]}
        errors = validate_custom_attribute_filter(attr.id, filter_config, organization, content_type)

        assert len(errors) == 0

    def test_validate_enum_filter_invalid_values(self, organization):
        content_type = ContentType.objects.get_for_model(Encounter)

        attr = CustomAttribute.objects.create(
            organization=organization,
            content_type=content_type,
            name="Priority",
            data_type=CustomAttribute.DataType.ENUM,
        )
        CustomAttributeEnum.objects.create(attribute=attr, label="High", value="high")

        filter_config = {"type": "enum", "values": ["high", "invalid_value"]}
        errors = validate_custom_attribute_filter(attr.id, filter_config, organization, content_type)

        assert "values" in errors
        assert "invalid_value" in errors["values"]

    def test_validate_date_filter_valid_range(self, organization):
        content_type = ContentType.objects.get_for_model(Encounter)

        attr = CustomAttribute.objects.create(
            organization=organization,
            content_type=content_type,
            name="Follow-up Date",
            data_type=CustomAttribute.DataType.DATE,
        )

        filter_config = {"type": "date", "operator": "range", "start": "2024-01-01", "end": "2024-12-31"}
        errors = validate_custom_attribute_filter(attr.id, filter_config, organization, content_type)

        assert len(errors) == 0

    def test_validate_date_filter_invalid_range(self, organization):
        content_type = ContentType.objects.get_for_model(Encounter)

        attr = CustomAttribute.objects.create(
            organization=organization,
            content_type=content_type,
            name="Follow-up Date",
            data_type=CustomAttribute.DataType.DATE,
        )

        filter_config = {"type": "date", "operator": "range", "start": "2024-12-31", "end": "2024-01-01"}
        errors = validate_custom_attribute_filter(attr.id, filter_config, organization, content_type)

        assert "range" in errors

    def test_validate_filter_wrong_content_type(self, organization):
        encounter_ct = ContentType.objects.get_for_model(Encounter)
        patient_ct = ContentType.objects.get_for_model(Patient)

        # Attribute is for Patient
        attr = CustomAttribute.objects.create(
            organization=organization,
            content_type=patient_ct,
            name="Patient Field",
            data_type=CustomAttribute.DataType.ENUM,
        )

        filter_config = {"type": "enum", "values": ["value1"]}
        errors = validate_custom_attribute_filter(attr.id, filter_config, organization, encounter_ct)

        assert "content_type" in errors

    def test_validate_filter_nonexistent_attribute(self, organization):
        content_type = ContentType.objects.get_for_model(Encounter)

        fake_id = uuid4()
        filter_config = {"type": "enum", "values": ["value1"]}
        errors = validate_custom_attribute_filter(fake_id, filter_config, organization, content_type)

        assert "attribute" in errors


@pytest.mark.django_db
class TestFilterPersistence:
    """Test saving and loading filters from preferences."""

    def test_save_filters_to_user_preference(self, user, organization):
        content_type = ContentType.objects.get_for_model(Encounter)

        attr = CustomAttribute.objects.create(
            organization=organization,
            content_type=content_type,
            name="Priority",
            data_type=CustomAttribute.DataType.ENUM,
        )

        CustomAttributeEnum.objects.create(attribute=attr, label="High", value="high")

        pref = ListViewPreference.objects.create(
            user=user,
            organization=organization,
            list_type=ListViewType.ENCOUNTER_LIST,
            scope=PreferenceScope.USER,
            visible_columns=["patient__first_name"],
        )

        filters = {"custom_attributes": {str(attr.id): {"type": "enum", "values": ["high"]}}, "model_fields": {}}

        updated_pref = save_filters_to_preference(pref, filters)

        assert updated_pref.saved_filters == filters
        assert str(attr.id) in updated_pref.saved_filters["custom_attributes"]

    def test_save_filters_to_org_preference(self, organization):
        content_type = ContentType.objects.get_for_model(Encounter)

        attr = CustomAttribute.objects.create(
            organization=organization,
            content_type=content_type,
            name="Priority",
            data_type=CustomAttribute.DataType.ENUM,
        )

        CustomAttributeEnum.objects.create(attribute=attr, label="High", value="high")

        pref = ListViewPreference.objects.create(
            user=None,
            organization=organization,
            list_type=ListViewType.ENCOUNTER_LIST,
            scope=PreferenceScope.ORGANIZATION,
            visible_columns=["patient__first_name"],
        )

        filters = {"custom_attributes": {str(attr.id): {"type": "enum", "values": ["high"]}}, "model_fields": {}}

        updated_pref = save_filters_to_preference(pref, filters)

        assert updated_pref.saved_filters == filters

    def test_parse_filters_from_request_with_saved(self, user, organization):
        content_type = ContentType.objects.get_for_model(Encounter)

        attr = CustomAttribute.objects.create(
            organization=organization,
            content_type=content_type,
            name="Priority",
            data_type=CustomAttribute.DataType.ENUM,
        )

        saved_filters = {"custom_attributes": {str(attr.id): {"values": ["high"]}}, "model_fields": {}}

        pref = ListViewPreference.objects.create(
            user=user,
            organization=organization,
            list_type=ListViewType.ENCOUNTER_LIST,
            scope=PreferenceScope.USER,
            visible_columns=["patient__first_name"],
            saved_filters=saved_filters,
        )

        factory = RequestFactory()
        request = factory.get("/")

        filters = parse_filters_from_request(request, pref)

        assert str(attr.id) in filters["custom_attributes"]
        assert filters["custom_attributes"][str(attr.id)]["values"] == ["high"]

    def test_parse_filters_request_overrides_saved(self, user, organization):
        content_type = ContentType.objects.get_for_model(Encounter)

        attr = CustomAttribute.objects.create(
            organization=organization,
            content_type=content_type,
            name="Priority",
            data_type=CustomAttribute.DataType.ENUM,
        )

        saved_filters = {"custom_attributes": {str(attr.id): {"values": ["high"]}}, "model_fields": {}}

        pref = ListViewPreference.objects.create(
            user=user,
            organization=organization,
            list_type=ListViewType.ENCOUNTER_LIST,
            scope=PreferenceScope.USER,
            visible_columns=["patient__first_name"],
            saved_filters=saved_filters,
        )

        factory = RequestFactory()
        attr_id_underscore = str(attr.id).replace("-", "_")
        request = factory.get(f"/?filter_attr_{attr_id_underscore}=low,medium")

        filters = parse_filters_from_request(request, pref)

        assert str(attr.id) in filters["custom_attributes"]
        assert "low" in filters["custom_attributes"][str(attr.id)]["values"]
        assert "medium" in filters["custom_attributes"][str(attr.id)]["values"]
        assert "high" not in filters["custom_attributes"][str(attr.id)]["values"]
