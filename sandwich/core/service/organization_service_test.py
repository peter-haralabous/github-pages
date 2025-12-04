import pytest

from sandwich.core.factories.organization import OrganizationFactory
from sandwich.core.models.organization import Organization
from sandwich.core.models.role import RoleName
from sandwich.core.service.organization_service import assign_organization_role
from sandwich.users.factories import UserFactory
from sandwich.users.models import User


@pytest.mark.django_db
def test_create_default_roles_and_perms() -> None:
    user = UserFactory.create()
    # `create_default_roles_and_perms` gets called by the factory
    org = OrganizationFactory.create()

    assert user.has_perm("view_organization", org) is False
    assert user.has_perm("change_organization", org) is False
    assert user.has_perm("create_encounter", org) is False
    assert user.has_perm("create_form", org) is False

    assign_organization_role(org, RoleName.OWNER, user)
    assert user.has_perm("view_organization", org) is True
    assert user.has_perm("change_organization", org) is True
    assert user.has_perm("delete_organization", org) is True
    assert user.has_perm("create_encounter", org) is True
    assert user.has_perm("create_patient", org) is True
    assert user.has_perm("create_invitation", org) is True
    assert user.has_perm("create_form", org) is True


def test_create_default_roles_and_perms_admin(organization: Organization) -> None:
    admin = UserFactory.create()
    assign_organization_role(organization, RoleName.ADMIN, admin)

    # Admin have these perms.
    assert admin.has_perm("view_organization", organization) is True
    assert admin.has_perm("change_organization", organization) is True
    assert admin.has_perm("create_encounter", organization) is True
    assert admin.has_perm("create_patient", organization) is True
    assert admin.has_perm("create_invitation", organization) is True
    assert admin.has_perm("create_form", organization) is True

    # They don't have these perms.
    assert admin.has_perm("delete_organization", organization) is False


def test_create_default_roles_and_perms_staff(provider: User, organization: Organization) -> None:
    # Staff have these perms.
    assert provider.has_perm("view_organization", organization) is True
    assert provider.has_perm("create_encounter", organization) is True
    assert provider.has_perm("create_patient", organization) is True
    assert provider.has_perm("create_invitation", organization) is True

    # They don't have these perms (not-exhaustive).
    assert provider.has_perm("change_organization", organization) is False
    assert provider.has_perm("delete_organization", organization) is False
    assert provider.has_perm("create_form", organization) is False
