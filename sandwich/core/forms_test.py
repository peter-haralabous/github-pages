import pytest

from sandwich.core.forms import DeleteConfirmationForm

pytestmark = pytest.mark.django_db


def test_account_delete_form_validation() -> None:
    """User must type DELETE exactly to delete their account."""
    form = DeleteConfirmationForm(data={"confirmation": "delete"})
    assert form.is_valid() is False

    form = DeleteConfirmationForm(data={"confirmation": "DELETE"})
    assert form.is_valid() is True
