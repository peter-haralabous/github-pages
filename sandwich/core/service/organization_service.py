from django.contrib.auth.models import Group
from django.db.models import QuerySet

from sandwich.core.models.organization import Organization
from sandwich.core.models.role import Role
from sandwich.core.models.role import RoleName
from sandwich.users.models import User


def get_provider_organizations(user: User) -> QuerySet[Organization]:
    """Returns a QuerySet of organizations that the user is a provider user in."""
    # TODO: move to user.provider_organizations?
    return Organization.objects.filter(
        role__group__user=user, role__name__in=(RoleName.OWNER, RoleName.STAFF)
    ).distinct()


def create_default_roles(organization: Organization) -> None:
    for role_name in [RoleName.OWNER, RoleName.STAFF, RoleName.PATIENT]:
        group = Group.objects.create(name=f"{role_name}_{organization.id}")
        Role.objects.create(organization=organization, name=role_name, group=group)
