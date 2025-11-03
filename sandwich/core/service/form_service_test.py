from sandwich.core.factories.form import FormFactory
from sandwich.core.models.organization import Organization
from sandwich.core.models.role import RoleName
from sandwich.core.service.organization_service import assign_organization_role
from sandwich.users.factories import UserFactory
from sandwich.users.models import User


def test_assign_default_form_permissions_owner(organization: Organization) -> None:
    """Ensure ORM.create() assigns default form permissions for organization's OWNER role."""
    owner = UserFactory.create()
    assign_organization_role(organization, RoleName.OWNER, owner)
    form = FormFactory.create(organization=organization)
    assert owner.has_perm("view_form", form) is True
    assert owner.has_perm("view_form", form) is True
    assert owner.has_perm("change_form", form) is True
    assert owner.has_perm("delete_form", form) is True


def test_assign_default_form_permissions_admin(organization: Organization) -> None:
    """Ensure ORM.create() assigns default form permissions for organization's ADMIN role."""
    admin = UserFactory.create()
    assign_organization_role(organization, RoleName.ADMIN, admin)
    form = FormFactory.create(organization=organization)
    assert admin.has_perm("view_form", form) is True
    assert admin.has_perm("change_form", form) is True
    assert admin.has_perm("delete_form", form) is True


def test_assign_default_form_permissions_staff(provider: User, organization: Organization) -> None:
    """Ensure ORM.create() assigns default form permissions for organization's STAFF role."""
    form = FormFactory.create(organization=organization)
    assert provider.has_perm("view_form", form) is True

    # Staff don't have these.
    assert provider.has_perm("change_form", form) is False
    assert provider.has_perm("delete_form", form) is False
