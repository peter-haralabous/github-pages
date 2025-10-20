import pytest

from sandwich.core.factories.organization import OrganizationFactory
from sandwich.core.models.role import RoleName
from sandwich.core.service.organization_service import assign_organization_role
from sandwich.users.factories import UserFactory


@pytest.mark.django_db
def test_create_default_roles_and_perms() -> None:
    user = UserFactory.create()
    # `create_default_roles_and_perms` gets called by the factory
    org = OrganizationFactory.create()

    assert user.has_perm("change_organization", org) is False
    assign_organization_role(org, RoleName.OWNER, user)
    assert user.has_perm("change_organization", org)
