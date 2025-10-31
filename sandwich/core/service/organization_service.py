import logging

from django.contrib.auth.models import Group
from django.db.models import QuerySet
from guardian.shortcuts import assign_perm

from sandwich.core.models.organization import Organization
from sandwich.core.models.role import Role
from sandwich.core.models.role import RoleName
from sandwich.users.models import User

logger = logging.getLogger(__name__)


def get_provider_organizations(user: User) -> QuerySet[Organization]:
    """Returns a QuerySet of organizations that the user is a provider user in."""
    logger.debug("Retrieving provider organizations for user", extra={"user_id": user.id})

    # TODO: move to user.provider_organizations?
    organizations = Organization.objects.filter(
        role__group__user=user, role__name__in=(RoleName.OWNER, RoleName.ADMIN, RoleName.STAFF)
    ).distinct()

    count = organizations.count()
    logger.debug(
        "Provider organizations retrieved",
        extra={"user_id": user.id, "organization_count": count},
    )

    return organizations


# TODO: Add org role permissions
DEFAULT_ORGANIZATION_ROLES: dict[str, list[str]] = {
    RoleName.OWNER: [
        "view_organization",
        "change_organization",
        "delete_organization",
        "create_encounter",
        "create_patient",
        "create_invitation",
        "create_form",
    ],
    RoleName.ADMIN: [
        "view_organization",
        "change_organization",
        "create_encounter",
        "create_patient",
        "create_invitation",
        "create_form",
    ],
    RoleName.STAFF: [
        "view_organization",
        "create_encounter",
        "create_patient",
        "create_invitation",
    ],
    RoleName.PATIENT: ["view_organization"],
}


def create_default_roles_and_perms(organization: Organization) -> None:
    logger.info("Creating default roles for organization", extra={"organization_id": organization.id})

    created_roles = []
    for role_name, org_perms in DEFAULT_ORGANIZATION_ROLES.items():
        group = Group.objects.create(name=f"{role_name}_{organization.id}")
        role = Role.objects.create(organization=organization, name=role_name, group=group)
        created_roles.append(role_name)

        for perm in org_perms:
            assign_perm(perm, group, organization)

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


def assign_organization_role(organization: Organization, role_name: str, user: User) -> None:
    """
    Assign user to a role in the organization.
    param role_name: str literal of RoleName, e.g. RoleName.OWNER
    """
    logger.debug(
        "Assigning role for organization",
        extra={
            "organization_id": organization.id,
            "role_name": role_name,
            "user_id": user.id,
        },
    )
    organization.role_set.get(name=role_name).group.user_set.add(user)


def get_active_organization(user: User, organization_id: str | None) -> Organization | None:
    if not organization_id:
        return None
    organizations = get_provider_organizations(user)

    for organization in organizations:
        if str(organization_id) == str(organization.id):
            return organization

    return None
