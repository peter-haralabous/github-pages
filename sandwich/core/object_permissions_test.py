import pytest
from guardian.shortcuts import assign_perm

from sandwich.core.factories.organization import OrganizationFactory
from sandwich.users.factories import UserFactory


@pytest.mark.django_db
def test_object_permissions_no_perms() -> None:
    user = UserFactory.create()
    organization = OrganizationFactory.create()

    assert user.has_perm("change_organization", organization) is False


@pytest.mark.django_db
def test_object_permissions_assign_perms() -> None:
    user = UserFactory.create()
    organization = OrganizationFactory.create()

    assign_perm("change_organization", user, organization)
    assert user.has_perm("change_organization", organization)

    # user only has permissions granted
    assert user.has_perm("delete_organization", organization) is False


@pytest.mark.django_db
def test_object_permissions_specific_to_object() -> None:
    user_a = UserFactory.create()
    user_b = UserFactory.create()
    organization_a = OrganizationFactory.create()
    organization_b = OrganizationFactory.create()

    # user_a is given permissions for org_a
    assign_perm("change_organization", user_a, organization_a)
    assert user_a.has_perm("change_organization", organization_a)

    assert user_a.has_perm("change_organization", organization_b) is False
    assert user_b.has_perm("change_organization", organization_a) is False
