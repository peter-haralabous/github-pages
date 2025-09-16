from django.contrib.auth.models import Group
from django.db import models

from sandwich.core.models.abstract import TimestampedModel
from sandwich.core.models.organization import Organization


# NOTE-NG: this is lightly adapted from bread
# we don't yet support custom roles, but we might in the future
class RoleName:
    """
    Well-known values of Role.name, as created by organization_service.create_default_roles

    Note that organizations can create custom roles. Consider looking up the role you want by RoleType instead.
    """

    OWNER = "owner"
    STAFF = "staff"
    PATIENT = "patient"


class Role(TimestampedModel):
    """
    The `Role` model serves as a bridge between django's `Group` and our `Organization` model.

    A one-to-one relationship with the `Group` model allows the Role to directly leverage Django's
    permissions framework, assigning specific permissions to each role.

    Each role is associated with an organization.
    """

    name = models.CharField(max_length=255)
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
    )

    # FIXME: why does mypy not see this by default?
    objects: models.Manager["Role"]

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "organization"],
                name="unique_role_name_per_organization",
            )
        ]
