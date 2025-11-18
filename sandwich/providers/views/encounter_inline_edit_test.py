"""Tests for encounter inline field editing functionality."""

import logging
import uuid

import pytest
from django.contrib.contenttypes.models import ContentType
from django.test import Client
from django.urls import reverse
from guardian.shortcuts import assign_perm

from sandwich.core.middleware import ConsentMiddleware
from sandwich.core.models import CustomAttribute
from sandwich.core.models import CustomAttributeEnum
from sandwich.core.models import CustomAttributeValue
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.organization import Organization
from sandwich.core.types import EMPTY_VALUE_DISPLAY
from sandwich.providers.views.encounter import _build_edit_form_context
from sandwich.providers.views.encounter import _get_field_display_value
from sandwich.users.factories import UserFactory
from sandwich.users.models import User


@pytest.fixture
def enum_attribute(organization: Organization) -> CustomAttribute:
    """Create a custom ENUM attribute for encounters."""
    return CustomAttribute.objects.create(
        organization=organization,
        content_type=ContentType.objects.get_for_model(Encounter),
        name="Priority",
        data_type=CustomAttribute.DataType.ENUM,
    )


@pytest.fixture
def enum_values(enum_attribute: CustomAttribute) -> dict[str, CustomAttributeEnum]:
    """Create enum values for the enum attribute."""
    low = CustomAttributeEnum.objects.create(attribute=enum_attribute, label="Low", value="low")
    high = CustomAttributeEnum.objects.create(attribute=enum_attribute, label="High", value="high")
    return {"low": low, "high": high}


@pytest.fixture
def date_attribute(organization: Organization) -> CustomAttribute:
    """Create a custom DATE attribute for encounters."""
    return CustomAttribute.objects.create(
        organization=organization,
        content_type=ContentType.objects.get_for_model(Encounter),
        name="Due Date",
        data_type=CustomAttribute.DataType.DATE,
    )


@pytest.fixture
def multi_enum_attribute(organization: Organization) -> CustomAttribute:
    """Create a multi-valued custom ENUM attribute for encounters."""
    return CustomAttribute.objects.create(
        organization=organization,
        content_type=ContentType.objects.get_for_model(Encounter),
        name="Tags",
        data_type=CustomAttribute.DataType.ENUM,
        is_multi=True,
    )


@pytest.fixture
def multi_enum_values(multi_enum_attribute: CustomAttribute) -> dict[str, CustomAttributeEnum]:
    """Create enum values for the multi-valued enum attribute."""
    urgent = CustomAttributeEnum.objects.create(attribute=multi_enum_attribute, label="Urgent", value="urgent")
    followup = CustomAttributeEnum.objects.create(attribute=multi_enum_attribute, label="Follow-up", value="followup")
    review = CustomAttributeEnum.objects.create(attribute=multi_enum_attribute, label="Review", value="review")
    return {"urgent": urgent, "followup": followup, "review": review}


@pytest.fixture
def user_without_change_perm(organization: Organization) -> User:
    """Create a user with view but not change permissions."""
    user = UserFactory.create(consents=ConsentMiddleware.required_policies)
    # Only assign view permissions, not change
    assign_perm("view_organization", user, organization)
    return user


class TestEncounterEditField:
    """Tests for GET endpoint to fetch inline edit form."""

    @pytest.mark.django_db
    def test_returns_edit_form_for_status_field(
        self, provider: User, organization: Organization, encounter: Encounter
    ) -> None:
        """Returns correct form HTML for status field."""
        client = Client()
        client.force_login(provider)
        url = reverse(
            "providers:encounter_edit_field",
            kwargs={
                "organization_id": organization.id,
                "encounter_id": encounter.id,
                "field_name": "status",
            },
        )

        response = client.get(url)

        assert response.status_code == 200
        content = response.content.decode()
        assert 'name="value"' in content
        assert EncounterStatus.IN_PROGRESS.value in content
        assert EncounterStatus.COMPLETED.value in content
        assert f'value="{encounter.status.value}"' in content
        assert "selected" in content

    @pytest.mark.django_db
    def test_returns_edit_form_for_custom_enum_attribute(
        self,
        provider: User,
        organization: Organization,
        encounter: Encounter,
        enum_attribute: CustomAttribute,
        enum_values: dict[str, CustomAttributeEnum],
    ) -> None:
        """Returns correct form HTML for custom ENUM attribute."""
        encounter.attributes.create(attribute=enum_attribute, value_enum=enum_values["high"])

        client = Client()
        client.force_login(provider)
        url = reverse(
            "providers:encounter_edit_field",
            kwargs={
                "organization_id": organization.id,
                "encounter_id": encounter.id,
                "field_name": str(enum_attribute.id),
            },
        )

        response = client.get(url)

        assert response.status_code == 200
        content = response.content.decode()
        assert 'name="value"' in content
        assert "Low" in content
        assert "High" in content
        assert f'value="{enum_values["high"].id}"' in content
        assert "selected" in content

    @pytest.mark.django_db
    def test_returns_edit_form_for_custom_date_attribute(
        self, provider: User, organization: Organization, encounter: Encounter, date_attribute: CustomAttribute
    ) -> None:
        """Returns correct form HTML for custom DATE attribute."""
        encounter.attributes.create(attribute=date_attribute, value_date="2024-12-25")

        client = Client()
        client.force_login(provider)
        url = reverse(
            "providers:encounter_edit_field",
            kwargs={
                "organization_id": organization.id,
                "encounter_id": encounter.id,
                "field_name": str(date_attribute.id),
            },
        )

        response = client.get(url)

        assert response.status_code == 200
        content = response.content.decode()
        assert 'type="date"' in content
        assert 'name="value"' in content
        assert "2024-12-25" in content

    @pytest.mark.django_db
    def test_returns_edit_form_for_custom_attribute_without_value(
        self, provider: User, organization: Organization, encounter: Encounter, enum_attribute: CustomAttribute
    ) -> None:
        """Returns form when custom attribute has no value set yet."""
        client = Client()
        client.force_login(provider)
        url = reverse(
            "providers:encounter_edit_field",
            kwargs={
                "organization_id": organization.id,
                "encounter_id": encounter.id,
                "field_name": str(enum_attribute.id),
            },
        )

        response = client.get(url)

        assert response.status_code == 200
        content = response.content.decode()
        assert 'name="value"' in content
        assert "selected" not in content or 'value=""' in content

    @pytest.mark.django_db
    def test_returns_400_for_invalid_field_name(
        self, provider: User, organization: Organization, encounter: Encounter
    ) -> None:
        """Returns 400 Bad Request for non-existent field."""
        client = Client()
        client.force_login(provider)
        url = reverse(
            "providers:encounter_edit_field",
            kwargs={
                "organization_id": organization.id,
                "encounter_id": encounter.id,
                "field_name": "nonexistent_field",
            },
        )

        response = client.get(url)

        assert response.status_code == 400
        assert b"Invalid field name" in response.content

    @pytest.mark.django_db
    def test_returns_400_for_custom_attribute_wrong_organization(
        self, provider: User, organization: Organization, encounter: Encounter, other_organization: Organization
    ) -> None:
        """Returns 400 when custom attribute belongs to different organization."""
        other_attribute = CustomAttribute.objects.create(
            organization=other_organization,
            content_type=ContentType.objects.get_for_model(Encounter),
            name="Other Attribute",
            data_type=CustomAttribute.DataType.ENUM,
        )

        client = Client()
        client.force_login(provider)
        url = reverse(
            "providers:encounter_edit_field",
            kwargs={
                "organization_id": organization.id,
                "encounter_id": encounter.id,
                "field_name": str(other_attribute.id),
            },
        )

        response = client.get(url)

        assert response.status_code == 400

    @pytest.mark.django_db
    def test_requires_change_encounter_permission(
        self, user_without_change_perm: User, organization: Organization, encounter: Encounter
    ) -> None:
        """Returns 404 (not 403) when user lacks change_encounter permission.

        User without permissions cannot see the encounter at all, so gets 404.
        """
        assign_perm("view_encounter", user_without_change_perm, encounter)

        client = Client()
        client.force_login(user_without_change_perm)
        url = reverse(
            "providers:encounter_edit_field",
            kwargs={
                "organization_id": organization.id,
                "encounter_id": encounter.id,
                "field_name": "status",
            },
        )

        response = client.get(url)

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_requires_authentication(self, organization: Organization, encounter: Encounter) -> None:
        """Redirects to login when not authenticated."""
        client = Client()
        url = reverse(
            "providers:encounter_edit_field",
            kwargs={
                "organization_id": organization.id,
                "encounter_id": encounter.id,
                "field_name": "status",
            },
        )

        response = client.get(url)

        assert response.status_code == 302
        assert "/login/" in response.url  # type: ignore[attr-defined]

    @pytest.mark.django_db
    def test_returns_404_for_nonexistent_encounter(self, provider: User, organization: Organization) -> None:
        """Returns 404 for non-existent encounter ID."""
        client = Client()
        client.force_login(provider)
        url = reverse(
            "providers:encounter_edit_field",
            kwargs={
                "organization_id": organization.id,
                "encounter_id": uuid.uuid4(),
                "field_name": "status",
            },
        )

        response = client.get(url)

        assert response.status_code == 404


class TestEncounterUpdateField:
    """Tests for POST endpoint to update inline field."""

    @pytest.mark.django_db
    def test_updates_status_field_successfully(
        self, provider: User, organization: Organization, encounter: Encounter
    ) -> None:
        """Updates status and returns OOB swap HTML."""
        original_status = encounter.status
        new_status = EncounterStatus.COMPLETED

        client = Client()
        client.force_login(provider)
        url = reverse(
            "providers:encounter_edit_field",
            kwargs={
                "organization_id": organization.id,
                "encounter_id": encounter.id,
                "field_name": "status",
            },
        )

        response = client.post(url, {"value": new_status.value})

        assert response.status_code == 200
        content = response.content.decode()
        assert f'id="encounter-{encounter.id}-status"' in content
        assert str(new_status.label) in content
        encounter.refresh_from_db()
        assert encounter.status == new_status
        assert encounter.status != original_status

    @pytest.mark.django_db
    def test_updates_custom_enum_attribute(
        self,
        provider: User,
        organization: Organization,
        encounter: Encounter,
        enum_attribute: CustomAttribute,
        enum_values: dict[str, CustomAttributeEnum],
    ) -> None:
        """Creates/updates CustomAttributeValue for ENUM type."""
        client = Client()
        client.force_login(provider)
        url = reverse(
            "providers:encounter_edit_field",
            kwargs={
                "organization_id": organization.id,
                "encounter_id": encounter.id,
                "field_name": str(enum_attribute.id),
            },
        )

        response = client.post(url, {"value": str(enum_values["high"].id)})

        assert response.status_code == 200
        content = response.content.decode()
        assert "High" in content
        assert f'id="encounter-{encounter.id}-{enum_attribute.id}"' in content

        # Verify database was updated
        attr_value = CustomAttributeValue.objects.get(
            attribute=enum_attribute,
            content_type=ContentType.objects.get_for_model(Encounter),
            object_id=encounter.id,
        )
        assert attr_value.value_enum == enum_values["high"]

    @pytest.mark.django_db
    def test_updates_existing_custom_enum_attribute(
        self,
        provider: User,
        organization: Organization,
        encounter: Encounter,
        enum_attribute: CustomAttribute,
        enum_values: dict[str, CustomAttributeEnum],
    ) -> None:
        """Updates existing CustomAttributeValue for ENUM type."""
        encounter.attributes.create(attribute=enum_attribute, value_enum=enum_values["low"])

        client = Client()
        client.force_login(provider)
        url = reverse(
            "providers:encounter_edit_field",
            kwargs={
                "organization_id": organization.id,
                "encounter_id": encounter.id,
                "field_name": str(enum_attribute.id),
            },
        )

        response = client.post(url, {"value": str(enum_values["high"].id)})

        assert response.status_code == 200

        # Verify database was updated
        attr_value = encounter.attributes.get(attribute=enum_attribute)
        assert attr_value.value_enum == enum_values["high"]

        # Verify only one value exists (update, not create)
        assert encounter.attributes.filter(attribute=enum_attribute).count() == 1

    @pytest.mark.django_db
    def test_updates_custom_date_attribute(
        self, provider: User, organization: Organization, encounter: Encounter, date_attribute: CustomAttribute
    ) -> None:
        """Creates/updates CustomAttributeValue for DATE type."""
        client = Client()
        client.force_login(provider)
        url = reverse(
            "providers:encounter_edit_field",
            kwargs={
                "organization_id": organization.id,
                "encounter_id": encounter.id,
                "field_name": str(date_attribute.id),
            },
        )

        response = client.post(url, {"value": "2024-12-25"})

        assert response.status_code == 200
        content = response.content.decode()
        assert "25 Dec 2024" in content

        # Verify database was updated
        attr_value = CustomAttributeValue.objects.get(
            attribute=date_attribute,
            content_type=ContentType.objects.get_for_model(Encounter),
            object_id=encounter.id,
        )
        assert attr_value.value_date is not None
        assert attr_value.value_date.isoformat() == "2024-12-25"

    @pytest.mark.django_db
    def test_returns_400_for_invalid_status_value(
        self, provider: User, organization: Organization, encounter: Encounter
    ) -> None:
        """Returns 400 for invalid status enum value."""
        client = Client()
        client.force_login(provider)
        url = reverse(
            "providers:encounter_edit_field",
            kwargs={
                "organization_id": organization.id,
                "encounter_id": encounter.id,
                "field_name": "status",
            },
        )

        response = client.post(url, {"value": "invalid_status_value"})

        assert response.status_code == 400

        # Verify database was not updated
        encounter.refresh_from_db()
        assert encounter.status == EncounterStatus.IN_PROGRESS

    @pytest.mark.django_db
    def test_returns_400_for_invalid_date_format(
        self, provider: User, organization: Organization, encounter: Encounter, date_attribute: CustomAttribute
    ) -> None:
        """Returns 400 for malformed date string."""
        client = Client()
        client.force_login(provider)
        url = reverse(
            "providers:encounter_edit_field",
            kwargs={
                "organization_id": organization.id,
                "encounter_id": encounter.id,
                "field_name": str(date_attribute.id),
            },
        )

        response = client.post(url, {"value": "not-a-date"})

        assert response.status_code == 400

        # Verify no value was created
        assert not encounter.attributes.filter(attribute=date_attribute).exists()

    @pytest.mark.django_db
    def test_returns_400_for_invalid_enum_value_id(
        self,
        provider: User,
        organization: Organization,
        encounter: Encounter,
        enum_attribute: CustomAttribute,
    ) -> None:
        """Returns 400 for non-existent enum value ID."""
        client = Client()
        client.force_login(provider)
        url = reverse(
            "providers:encounter_edit_field",
            kwargs={
                "organization_id": organization.id,
                "encounter_id": encounter.id,
                "field_name": str(enum_attribute.id),
            },
        )

        response = client.post(url, {"value": str(uuid.uuid4())})

        assert response.status_code == 400

    @pytest.mark.django_db
    def test_returns_400_for_invalid_field_name(
        self, provider: User, organization: Organization, encounter: Encounter
    ) -> None:
        """Returns 400 for non-existent field name."""
        client = Client()
        client.force_login(provider)
        url = reverse(
            "providers:encounter_edit_field",
            kwargs={
                "organization_id": organization.id,
                "encounter_id": encounter.id,
                "field_name": "nonexistent_field",
            },
        )

        response = client.post(url, {"value": "some_value"})

        assert response.status_code == 400

    @pytest.mark.django_db
    def test_requires_change_encounter_permission(
        self, user_without_change_perm: User, organization: Organization, encounter: Encounter
    ) -> None:
        """Returns 404 (not 403) when user lacks change_encounter permission.

        User without permissions cannot see the encounter at all, so gets 404.
        """
        assign_perm("view_encounter", user_without_change_perm, encounter)

        client = Client()
        client.force_login(user_without_change_perm)
        url = reverse(
            "providers:encounter_edit_field",
            kwargs={
                "organization_id": organization.id,
                "encounter_id": encounter.id,
                "field_name": "status",
            },
        )

        response = client.post(url, {"value": EncounterStatus.COMPLETED.value})

        # Without change permission, authorization fails and returns 404
        assert response.status_code == 404

        # Verify database was not updated
        encounter.refresh_from_db()
        assert encounter.status == EncounterStatus.IN_PROGRESS

    @pytest.mark.django_db
    def test_logs_audit_trail(self, provider: User, organization: Organization, encounter: Encounter, caplog) -> None:
        """Logs field update with user, encounter, field, and value."""
        caplog.set_level(logging.INFO)

        client = Client()
        client.force_login(provider)
        url = reverse(
            "providers:encounter_edit_field",
            kwargs={
                "organization_id": organization.id,
                "encounter_id": encounter.id,
                "field_name": "status",
            },
        )

        response = client.post(url, {"value": EncounterStatus.COMPLETED.value})

        assert response.status_code == 200

        # Verify audit log was created (the logs use JSON format so just check the message)
        assert "Encounter field updated via inline edit" in caplog.text

    @pytest.mark.django_db
    def test_returns_oob_swap_with_correct_cell_id(
        self, provider: User, organization: Organization, encounter: Encounter
    ) -> None:
        """Returns HTML with hx-swap-oob=true and correct cell ID."""
        client = Client()
        client.force_login(provider)
        url = reverse(
            "providers:encounter_edit_field",
            kwargs={
                "organization_id": organization.id,
                "encounter_id": encounter.id,
                "field_name": "status",
            },
        )

        response = client.post(url, {"value": EncounterStatus.COMPLETED.value})

        assert response.status_code == 200
        content = response.content.decode()

        # Verify correct cell ID format
        expected_cell_id = f"encounter-{encounter.id}-status"
        assert f'id="{expected_cell_id}"' in content

    @pytest.mark.django_db
    def test_get_returns_edit_form(self, provider: User, organization: Organization, encounter: Encounter) -> None:
        """GET request returns the edit form."""
        client = Client()
        client.force_login(provider)
        url = reverse(
            "providers:encounter_edit_field",
            kwargs={
                "organization_id": organization.id,
                "encounter_id": encounter.id,
                "field_name": "status",
            },
        )

        response = client.get(url)

        assert response.status_code == 200
        content = response.content.decode()
        assert 'name="value"' in content


class TestInlineEditHelperFunctions:
    """Tests for helper functions used in inline editing."""

    @pytest.mark.django_db
    def test_get_field_display_value_for_status(self, encounter: Encounter, organization: Organization) -> None:
        """Test _get_field_display_value for status field."""
        encounter.status = EncounterStatus.IN_PROGRESS
        encounter.save()

        display = _get_field_display_value(encounter, "status", organization)

        assert display == EncounterStatus.IN_PROGRESS.label

    @pytest.mark.django_db
    def test_get_field_display_value_for_custom_enum_attribute(
        self, encounter: Encounter, organization: Organization, enum_attribute: CustomAttribute, enum_values
    ) -> None:
        """Test _get_field_display_value for custom enum attributes."""
        # Set value
        encounter.attributes.create(attribute=enum_attribute, value_enum=enum_values["high"])

        display = _get_field_display_value(encounter, str(enum_attribute.id), organization)

        assert display == "High"

    @pytest.mark.django_db
    def test_get_field_display_value_for_custom_date_attribute(
        self, encounter: Encounter, organization: Organization, date_attribute: CustomAttribute
    ) -> None:
        """Test _get_field_display_value for custom date attributes."""
        # Set value
        encounter.attributes.create(attribute=date_attribute, value_date="2024-12-25")

        display = _get_field_display_value(encounter, str(date_attribute.id), organization)

        assert display == "25 Dec 2024"

    @pytest.mark.django_db
    def test_get_field_display_value_returns_placeholder_for_missing_custom_attribute(
        self, encounter: Encounter, organization: Organization
    ) -> None:
        """Test _get_field_display_value returns placeholder for non-existent custom attribute."""
        display = _get_field_display_value(encounter, str(uuid.uuid4()), organization)

        assert display == EMPTY_VALUE_DISPLAY

    @pytest.mark.django_db
    def test_get_field_display_value_returns_placeholder_for_unset_custom_attribute(
        self, encounter: Encounter, organization: Organization, enum_attribute: CustomAttribute
    ) -> None:
        """Test _get_field_display_value returns placeholder when custom attribute has no value."""
        # Don't set any value
        display = _get_field_display_value(encounter, str(enum_attribute.id), organization)

        assert display == EMPTY_VALUE_DISPLAY

    @pytest.mark.django_db
    def test_get_field_display_value_for_multi_valued_enum_attribute(
        self,
        encounter: Encounter,
        organization: Organization,
        multi_enum_attribute: CustomAttribute,
        multi_enum_values,
    ) -> None:
        """Test _get_field_display_value for multi-valued custom enum attributes."""
        # Set multiple values
        encounter.attributes.create(attribute=multi_enum_attribute, value_enum=multi_enum_values["urgent"])
        encounter.attributes.create(attribute=multi_enum_attribute, value_enum=multi_enum_values["review"])

        display = _get_field_display_value(encounter, str(multi_enum_attribute.id), organization)

        assert display == "Review, Urgent"  # Alphabetical order

    @pytest.mark.django_db
    def test_get_field_display_value_returns_placeholder_for_unset_multi_valued_attribute(
        self, encounter: Encounter, organization: Organization, multi_enum_attribute: CustomAttribute
    ) -> None:
        """Test _get_field_display_value returns placeholder when multi-valued attribute has no values."""
        display = _get_field_display_value(encounter, str(multi_enum_attribute.id), organization)

        assert display == EMPTY_VALUE_DISPLAY

    @pytest.mark.django_db
    def test_build_edit_form_context_for_status(self, encounter: Encounter, organization: Organization) -> None:
        """Test _build_edit_form_context for status field."""
        context = _build_edit_form_context(encounter, "status", organization)

        assert context is not None
        assert context["field_type"] == "select"
        assert context["field_label"] == "Status"
        assert context["current_value"] == encounter.status.value
        choices = context["choices"]
        assert isinstance(choices, list)
        assert len(choices) > 0
        assert any(choice[0] == EncounterStatus.IN_PROGRESS.value for choice in choices)

    @pytest.mark.django_db
    def test_build_edit_form_context_for_custom_enum(
        self, encounter: Encounter, organization: Organization, enum_attribute: CustomAttribute, enum_values
    ) -> None:
        """Test _build_edit_form_context for custom enum attribute."""
        # Set value
        encounter.attributes.create(attribute=enum_attribute, value_enum=enum_values["high"])

        context = _build_edit_form_context(encounter, str(enum_attribute.id), organization)

        assert context is not None
        assert context["field_type"] == "select"
        assert context["field_label"] == "Priority"
        assert context["current_value"] == str(enum_values["high"].id)
        choices = context["choices"]
        assert isinstance(choices, list)
        assert len(choices) == 2

    @pytest.mark.django_db
    def test_build_edit_form_context_for_custom_date(
        self, encounter: Encounter, organization: Organization, date_attribute: CustomAttribute
    ) -> None:
        """Test _build_edit_form_context for custom date attribute."""
        # Set value
        encounter.attributes.create(attribute=date_attribute, value_date="2024-12-25")

        context = _build_edit_form_context(encounter, str(date_attribute.id), organization)

        assert context is not None
        assert context["field_type"] == "date"
        assert context["field_label"] == "Due Date"
        assert context["current_value"] == "2024-12-25"
        assert context["choices"] == []

    @pytest.mark.django_db
    def test_build_edit_form_context_for_multi_valued_enum(
        self,
        encounter: Encounter,
        organization: Organization,
        multi_enum_attribute: CustomAttribute,
        multi_enum_values,
    ) -> None:
        """Test _build_edit_form_context for multi-valued custom enum attribute."""
        # Set multiple values
        encounter.attributes.create(attribute=multi_enum_attribute, value_enum=multi_enum_values["urgent"])
        encounter.attributes.create(attribute=multi_enum_attribute, value_enum=multi_enum_values["followup"])

        context = _build_edit_form_context(encounter, str(multi_enum_attribute.id), organization)

        assert context is not None
        assert context["field_type"] == "multi-select"
        assert context["field_label"] == "Tags"
        # Should return list of selected IDs
        assert isinstance(context["current_value"], list)
        assert str(multi_enum_values["urgent"].id) in context["current_value"]
        assert str(multi_enum_values["followup"].id) in context["current_value"]
        assert str(multi_enum_values["review"].id) not in context["current_value"]
        choices = context["choices"]
        assert isinstance(choices, list)
        assert len(choices) == 3

    @pytest.mark.django_db
    def test_build_edit_form_context_returns_none_for_invalid_field(
        self, encounter: Encounter, organization: Organization
    ) -> None:
        """Test _build_edit_form_context returns None for invalid field."""
        context = _build_edit_form_context(encounter, "nonexistent_field", organization)

        assert context is None
