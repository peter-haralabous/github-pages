import logging

from django.contrib.auth.models import Group
from django.db.models import QuerySet

from sandwich.core.models.organization import Organization
from sandwich.core.models.role import Role
from sandwich.core.models.role import RoleName
from sandwich.users.models import User

logger = logging.getLogger(__name__)


def get_provider_organizations(user: User) -> QuerySet[Organization]:
    """Returns a QuerySet of organizations that the user is a provider user in."""
    logger.debug("Retrieving provider organizations for user", extra={"user_id": user.id})

    # TODO: move to user.provider_organizations?
    # FIXME: why does mypy think that `role` isn't an Organization field?
    organizations = Organization.objects.filter(  # type: ignore[misc]
        role__group__user=user, role__name__in=(RoleName.OWNER, RoleName.STAFF)
    ).distinct()

    count = organizations.count()
    logger.debug(
        "Provider organizations retrieved",
        extra={"user_id": user.id, "organization_count": count},
    )

    return organizations


def create_default_roles(organization: Organization) -> None:
    logger.info("Creating default roles for organization", extra={"organization_id": organization.id})

    created_roles = []
    for role_name in [RoleName.OWNER, RoleName.STAFF, RoleName.PATIENT]:
        group = Group.objects.create(name=f"{role_name}_{organization.id}")
        role = Role.objects.create(organization=organization, name=role_name, group=group)
        created_roles.append(role_name)
        logger.debug(
            "Created role for organization",
            extra={
                "organization_id": organization.id,
                "role_name": role_name,
                "group_id": group.id,
                "role_id": role.id,
            },
        )

    logger.info(
        "Default roles created successfully",
        extra={"organization_id": organization.id, "roles_created": created_roles},
    )
