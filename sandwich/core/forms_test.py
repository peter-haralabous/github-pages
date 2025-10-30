import pytest

from sandwich.core.factories.organization import OrganizationFactory
from sandwich.core.forms import DeleteConfirmationForm
from sandwich.core.models import ListViewType
from sandwich.providers.views.list_preferences import ListPreferenceForm

pytestmark = pytest.mark.django_db


def test_account_delete_form_validation() -> None:
    """User must type DELETE exactly to delete their account."""
    form = DeleteConfirmationForm(data={"confirmation": "delete"})
    assert form.is_valid() is False

    form = DeleteConfirmationForm(data={"confirmation": "DELETE"})
    assert form.is_valid() is True


class TestListPreferenceForm:
    def test_form_with_valid_data(self) -> None:
        org = OrganizationFactory.create()
        available_columns = [
            {"value": "patient__first_name", "label": "Patient Name"},
            {"value": "patient__email", "label": "Email"},
            {"value": "created_at", "label": "Created"},
        ]

        form = ListPreferenceForm(
            data={
                "visible_columns": ["patient__first_name", "patient__email"],
                "default_sort": "-created_at",
                "items_per_page": "25",
            },
            list_type=ListViewType.ENCOUNTER_LIST,
            available_columns=available_columns,
            organization=org,
        )

        assert form.is_valid()
        assert form.cleaned_data["visible_columns"] == ["patient__first_name", "patient__email"]
        assert form.cleaned_data["default_sort"] == "-created_at"
        assert form.cleaned_data["items_per_page"] == 25

    def test_form_with_invalid_column(self) -> None:
        org = OrganizationFactory.create()
        available_columns = [
            {"value": "patient__first_name", "label": "Patient Name"},
            {"value": "patient__email", "label": "Email"},
        ]

        form = ListPreferenceForm(
            data={
                "visible_columns": ["patient__first_name", "invalid_column"],
                "default_sort": "",
                "items_per_page": "25",
            },
            list_type=ListViewType.ENCOUNTER_LIST,
            available_columns=available_columns,
            organization=org,
        )

        assert not form.is_valid()
        assert "visible_columns" in form.errors

    def test_form_with_invalid_sort_field(self) -> None:
        org = OrganizationFactory.create()
        available_columns = [
            {"value": "patient__first_name", "label": "Patient Name"},
            {"value": "patient__email", "label": "Email"},
        ]

        form = ListPreferenceForm(
            data={
                "visible_columns": ["patient__first_name"],
                "default_sort": "invalid_field",
                "items_per_page": "25",
            },
            list_type=ListViewType.ENCOUNTER_LIST,
            available_columns=available_columns,
            organization=org,
        )

        assert not form.is_valid()
        assert "default_sort" in form.errors

    def test_form_with_descending_sort(self) -> None:
        org = OrganizationFactory.create()
        available_columns = [
            {"value": "patient__first_name", "label": "Patient Name"},
            {"value": "created_at", "label": "Created"},
        ]

        form = ListPreferenceForm(
            data={
                "visible_columns": ["patient__first_name"],
                "default_sort": "-created_at",
                "items_per_page": "25",
            },
            list_type=ListViewType.ENCOUNTER_LIST,
            available_columns=available_columns,
            organization=org,
        )

        assert form.is_valid()
        assert form.cleaned_data["default_sort"] == "-created_at"

    def test_form_with_empty_sort(self) -> None:
        org = OrganizationFactory.create()
        available_columns = [
            {"value": "patient__first_name", "label": "Patient Name"},
        ]

        form = ListPreferenceForm(
            data={
                "visible_columns": ["patient__first_name"],
                "default_sort": "",
                "items_per_page": "25",
            },
            list_type=ListViewType.ENCOUNTER_LIST,
            available_columns=available_columns,
            organization=org,
        )

        assert form.is_valid()
        assert form.cleaned_data["default_sort"] == ""

    def test_form_with_invalid_items_per_page(self) -> None:
        org = OrganizationFactory.create()
        available_columns = [
            {"value": "patient__first_name", "label": "Patient Name"},
        ]

        form = ListPreferenceForm(
            data={
                "visible_columns": ["patient__first_name"],
                "default_sort": "",
                "items_per_page": "999",  # Invalid value
            },
            list_type=ListViewType.ENCOUNTER_LIST,
            available_columns=available_columns,
            organization=org,
        )

        assert not form.is_valid()
        assert "items_per_page" in form.errors

    def test_form_with_empty_visible_columns(self) -> None:
        org = OrganizationFactory.create()
        available_columns = [
            {"value": "patient__first_name", "label": "Patient Name"},
        ]

        form = ListPreferenceForm(
            data={
                "visible_columns": [],
                "default_sort": "",
                "items_per_page": "50",
            },
            list_type=ListViewType.ENCOUNTER_LIST,
            available_columns=available_columns,
            organization=org,
        )

        assert form.is_valid()
        assert form.cleaned_data["visible_columns"] == []
        assert form.cleaned_data["items_per_page"] == 50

    def test_form_preserves_column_order(self) -> None:
        org = OrganizationFactory.create()
        available_columns = [
            {"value": "patient__first_name", "label": "Patient Name"},
            {"value": "patient__email", "label": "Email"},
            {"value": "created_at", "label": "Created"},
        ]

        form = ListPreferenceForm(
            data={
                "visible_columns": ["created_at", "patient__first_name", "patient__email"],
                "default_sort": "",
                "items_per_page": "25",
            },
            list_type=ListViewType.ENCOUNTER_LIST,
            available_columns=available_columns,
            organization=org,
        )

        assert form.is_valid()
        assert form.cleaned_data["visible_columns"] == [
            "created_at",
            "patient__first_name",
            "patient__email",
        ]

    def test_form_preserves_patient_list_order(self) -> None:
        org = OrganizationFactory.create()
        available_columns = [
            {"value": "first_name", "label": "Name"},
            {"value": "email", "label": "Email"},
            {"value": "created_at", "label": "Created"},
        ]

        submitted = ["email", "first_name", "created_at"]
        form = ListPreferenceForm(
            data={
                "visible_columns": submitted,
                "default_sort": "-created_at",
                "items_per_page": "25",
            },
            list_type=ListViewType.PATIENT_LIST,
            available_columns=available_columns,
            organization=org,
        )
        assert form.is_valid(), form.errors
        assert form.cleaned_data["visible_columns"] == submitted
