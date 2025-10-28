"""Unit tests for list preference model and service."""

import pytest
from django.db import IntegrityError

from sandwich.core.factories.organization import OrganizationFactory
from sandwich.core.models import ListViewPreference
from sandwich.core.models import ListViewType
from sandwich.core.models import PreferenceScope
from sandwich.core.service.list_preference_service import get_available_columns
from sandwich.core.service.list_preference_service import get_default_columns
from sandwich.core.service.list_preference_service import get_default_sort
from sandwich.core.service.list_preference_service import get_list_view_preference
from sandwich.core.service.list_preference_service import reset_list_view_preference
from sandwich.core.service.list_preference_service import save_list_view_preference
from sandwich.users.factories import UserFactory


@pytest.mark.django_db
class TestListViewPreferenceModel:
    """Test the ListViewPreference model constraints and behavior."""

    def test_create_user_preference(self):
        """User can create a preference for a list type."""
        user = UserFactory.create()
        org = OrganizationFactory.create()

        pref = ListViewPreference.objects.create(
            user=user,
            organization=org,
            list_type=ListViewType.ENCOUNTER_LIST,
            scope=PreferenceScope.USER,
            visible_columns=["patient__first_name", "patient__email"],
            default_sort="-updated_at",
            items_per_page=50,
        )

        assert pref.user == user
        assert pref.organization == org
        assert pref.list_type == ListViewType.ENCOUNTER_LIST
        assert pref.scope == PreferenceScope.USER
        assert len(pref.visible_columns) == 2
        assert pref.items_per_page == 50

    def test_user_preference_unique_constraint(self):
        """User can only have one preference per list type in an organization."""
        user = UserFactory.create()
        org = OrganizationFactory.create()

        ListViewPreference.objects.create(
            user=user,
            organization=org,
            list_type=ListViewType.ENCOUNTER_LIST,
            scope=PreferenceScope.USER,
        )

        with pytest.raises(IntegrityError):
            ListViewPreference.objects.create(
                user=user,
                organization=org,
                list_type=ListViewType.ENCOUNTER_LIST,
                scope=PreferenceScope.USER,
            )

    def test_org_preference_unique_constraint(self):
        """Organization can only have one default preference per list type."""
        org = OrganizationFactory.create()

        ListViewPreference.objects.create(
            organization=org,
            list_type=ListViewType.ENCOUNTER_LIST,
            scope=PreferenceScope.ORGANIZATION,
            user=None,
        )

        with pytest.raises(IntegrityError):
            ListViewPreference.objects.create(
                organization=org,
                list_type=ListViewType.ENCOUNTER_LIST,
                scope=PreferenceScope.ORGANIZATION,
                user=None,
            )

    def test_user_can_have_different_preferences_for_different_lists(self):
        """User can have different preferences for encounter_list and patient_list."""
        user = UserFactory.create()
        org = OrganizationFactory.create()

        encounter_pref = ListViewPreference.objects.create(
            user=user,
            organization=org,
            list_type=ListViewType.ENCOUNTER_LIST,
            scope=PreferenceScope.USER,
            visible_columns=["patient__first_name"],
        )

        patient_pref = ListViewPreference.objects.create(
            user=user,
            organization=org,
            list_type=ListViewType.PATIENT_LIST,
            scope=PreferenceScope.USER,
            visible_columns=["first_name", "email"],
        )

        assert encounter_pref.id != patient_pref.id
        assert encounter_pref.visible_columns != patient_pref.visible_columns

    def test_scope_user_consistency_constraint(self):
        """User-scoped preference must have a user, org-scoped must not."""
        org = OrganizationFactory.create()

        # This should fail - USER scope without user
        with pytest.raises(IntegrityError):
            ListViewPreference.objects.create(
                organization=org,
                list_type=ListViewType.ENCOUNTER_LIST,
                scope=PreferenceScope.USER,
                user=None,
            )

    def test_str_representation(self):
        """Test __str__ method for both scopes."""
        user = UserFactory.create()
        org = OrganizationFactory.create()

        user_pref = ListViewPreference.objects.create(
            user=user,
            organization=org,
            list_type=ListViewType.ENCOUNTER_LIST,
            scope=PreferenceScope.USER,
        )
        assert str(user) in str(user_pref)
        assert ListViewType.ENCOUNTER_LIST.value in str(user_pref)

        org_pref = ListViewPreference.objects.create(
            organization=org,
            list_type=ListViewType.PATIENT_LIST,
            scope=PreferenceScope.ORGANIZATION,
            user=None,
        )
        assert str(org) in str(org_pref)
        assert "org default" in str(org_pref)


@pytest.mark.django_db
class TestListPreferenceService:
    """Test the list preference service functions."""

    def test_get_preference_returns_defaults_when_no_preferences_exist(self):
        """When no preferences exist, return unsaved preference with hardcoded defaults."""
        user = UserFactory.create()
        org = OrganizationFactory.create()
        ListViewPreference.objects.filter(organization=org).delete()

        pref = get_list_view_preference(user, org, ListViewType.ENCOUNTER_LIST)

        assert pref is not None
        assert pref.visible_columns == get_default_columns(ListViewType.ENCOUNTER_LIST)
        assert pref.default_sort == get_default_sort(ListViewType.ENCOUNTER_LIST)
        assert pref.items_per_page == 25

    def test_get_preference_returns_user_preference_when_exists(self):
        """User preference is returned when it exists."""
        user = UserFactory.create()
        org = OrganizationFactory.create()

        user_pref = save_list_view_preference(
            organization=org,
            list_type=ListViewType.ENCOUNTER_LIST,
            user=user,
            visible_columns=["patient__first_name"],
        )

        pref = get_list_view_preference(user, org, ListViewType.ENCOUNTER_LIST)

        assert pref is not None
        assert pref.id == user_pref.id
        assert pref.scope == PreferenceScope.USER

    def test_preference_inheritance(self):
        """User preferences override organization defaults."""
        user = UserFactory.create()
        org = OrganizationFactory.create()

        # Create org default
        org_pref = save_list_view_preference(
            organization=org,
            list_type=ListViewType.ENCOUNTER_LIST,
            visible_columns=["patient__first_name", "patient__email"],
            items_per_page=10,
        )

        # User should get org default
        pref = get_list_view_preference(user, org, ListViewType.ENCOUNTER_LIST)
        assert pref is not None
        assert pref.id == org_pref.id
        assert pref.items_per_page == 10

        # Create user preference
        user_pref = save_list_view_preference(
            organization=org,
            list_type=ListViewType.ENCOUNTER_LIST,
            user=user,
            visible_columns=["patient__first_name"],
            items_per_page=50,
        )

        # User should now get their own preference
        pref = get_list_view_preference(user, org, ListViewType.ENCOUNTER_LIST)
        assert pref is not None
        assert pref.id == user_pref.id
        assert pref.items_per_page == 50

    def test_save_user_preference_creates_new_preference(self):
        """save_list_view_preference creates a new user preference."""
        user = UserFactory.create()
        org = OrganizationFactory.create()

        pref = save_list_view_preference(
            organization=org,
            list_type=ListViewType.ENCOUNTER_LIST,
            user=user,
            visible_columns=["patient__first_name", "patient__email"],
            default_sort="-created_at",
            items_per_page=100,
        )

        assert pref.user == user
        assert pref.organization == org
        assert len(pref.visible_columns) == 2
        assert pref.default_sort == "-created_at"
        assert pref.items_per_page == 100

    def test_save_user_preference_updates_existing(self):
        """save_list_view_preference updates existing user preference."""
        user = UserFactory.create()
        org = OrganizationFactory.create()

        # Create initial preference
        pref1 = save_list_view_preference(
            organization=org,
            list_type=ListViewType.ENCOUNTER_LIST,
            user=user,
            visible_columns=["patient__first_name"],
            items_per_page=25,
        )

        # Update it
        pref2 = save_list_view_preference(
            organization=org,
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
            user=user, organization=org, list_type=ListViewType.ENCOUNTER_LIST
        ).count()
        assert count == 1

    def test_save_organization_default(self):
        """save_list_view_preference creates org preference."""
        org = OrganizationFactory.create()

        pref = save_list_view_preference(
            organization=org,
            list_type=ListViewType.ENCOUNTER_LIST,
            visible_columns=["patient__first_name", "patient__email"],
            default_sort="-updated_at",
        )

        assert pref.organization == org
        assert pref.user is None
        assert pref.scope == PreferenceScope.ORGANIZATION
        assert len(pref.visible_columns) == 2

    def test_reset_user_preference(self):
        """reset_list_view_preference deletes user preference causing fallback."""
        user = UserFactory.create()
        org = OrganizationFactory.create()

        # Create user preference
        save_list_view_preference(
            organization=org,
            list_type=ListViewType.ENCOUNTER_LIST,
            user=user,
            visible_columns=["patient__first_name"],
        )

        # Create org default
        org_pref = save_list_view_preference(
            organization=org,
            list_type=ListViewType.ENCOUNTER_LIST,
            visible_columns=["patient__first_name", "patient__email"],
        )

        # User should get their preference
        pref = get_list_view_preference(user, org, ListViewType.ENCOUNTER_LIST)
        assert pref is not None
        assert pref.scope == PreferenceScope.USER

        # Reset user preference
        reset_list_view_preference(organization=org, list_type=ListViewType.ENCOUNTER_LIST, user=user)

        # User should now get org default
        pref = get_list_view_preference(user, org, ListViewType.ENCOUNTER_LIST)
        assert pref is not None
        assert pref.id == org_pref.id
        assert pref.scope == PreferenceScope.ORGANIZATION

    def test_get_default_columns(self):
        """get_default_columns returns correct defaults for each list type."""
        encounter_cols = get_default_columns(ListViewType.ENCOUNTER_LIST)
        assert "patient__first_name" in encounter_cols
        assert "patient__email" in encounter_cols
        assert len(encounter_cols) > 0

        patient_cols = get_default_columns(ListViewType.PATIENT_LIST)
        assert "first_name" in patient_cols
        assert "email" in patient_cols
        assert len(patient_cols) > 0

    def test_get_default_sort(self):
        """get_default_sort returns correct defaults for each list type."""
        encounter_sort = get_default_sort(ListViewType.ENCOUNTER_LIST)
        assert encounter_sort == "-updated_at"

        patient_sort = get_default_sort(ListViewType.PATIENT_LIST)
        assert patient_sort == "-updated_at"

    def test_get_available_columns(self):
        """get_available_columns returns all available columns with labels."""
        encounter_cols = get_available_columns(ListViewType.ENCOUNTER_LIST)
        assert len(encounter_cols) > 0
        assert all("value" in col and "label" in col for col in encounter_cols)

        patient_cols = get_available_columns(ListViewType.PATIENT_LIST)
        assert len(patient_cols) > 0
        assert all("value" in col and "label" in col for col in patient_cols)

    def test_inactive_preferences_not_returned(self):
        """Deleted (previously inactive) preferences fall back to defaults."""
        user = UserFactory.create()
        org = OrganizationFactory.create()
        ListViewPreference.objects.filter(organization=org).delete()

        # Simulate previously inactive preference by creating then deleting
        temp_pref = ListViewPreference.objects.create(
            user=user,
            organization=org,
            list_type=ListViewType.ENCOUNTER_LIST,
            scope=PreferenceScope.USER,
        )
        temp_pref.delete()

        pref = get_list_view_preference(user, org, ListViewType.ENCOUNTER_LIST)
        assert pref is not None
        # Preference falls back to defaults regardless of persistence state
        assert pref.visible_columns == get_default_columns(ListViewType.ENCOUNTER_LIST)

    def test_different_orgs_have_separate_preferences(self):
        """User preferences are scoped per organization."""
        user = UserFactory.create()
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
