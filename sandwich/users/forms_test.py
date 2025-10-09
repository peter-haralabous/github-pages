"""Module for all Form Tests."""

from django.utils.translation import gettext_lazy as _

from sandwich.users.forms import AccountDeleteForm
from sandwich.users.forms import UserAdminCreationForm
from sandwich.users.models import User


class TestUserAdminCreationForm:
    """
    Test class for all tests related to the UserAdminCreationForm
    """

    def test_username_validation_error_msg(self, user: User):
        """
        Tests UserAdminCreation Form's unique validator functions correctly by testing:
            1) A new user with an existing username cannot be added.
            2) Only 1 error is raised by the UserCreation Form
            3) The desired error message is raised
        """

        # The user already exists,
        # hence cannot be created.
        form = UserAdminCreationForm(
            {
                "email": user.email,
                "password1": user.password,
                "password2": user.password,
            },
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "email" in form.errors
        assert form.errors["email"][0] == _("This email has already been taken.")


def test_account_delete_form_validation() -> None:
    """User must type DELETE exactly to delete their account."""
    form = AccountDeleteForm(data={"confirmation": "delete"})
    assert form.is_valid() is False

    form = AccountDeleteForm(data={"confirmation": "DELETE"})
    assert form.is_valid() is True
