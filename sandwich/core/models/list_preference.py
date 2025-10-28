"""List view preference models for customizable table views."""

import logging

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from sandwich.core.models.abstract import BaseModel

logger = logging.getLogger(__name__)


class ListViewType(models.TextChoices):
    """Types of list views that support preferences."""

    ENCOUNTER_LIST = "encounter_list", _("Encounter List")
    PATIENT_LIST = "patient_list", _("Patient List")
    # Future: task_list, etc.


class PreferenceScope(models.TextChoices):
    """Scope of the preference - user or organization."""

    USER = "user", _("User")
    ORGANIZATION = "organization", _("Organization")


class ListViewPreference(BaseModel):
    """
    Stores user and organization preferences for list views.

    User preferences override organization preferences.
    Each user can have one preference per list type.
    Each organization can have one default preference per list type.
    """

    scope = models.CharField(
        max_length=20,
        choices=PreferenceScope,
        default=PreferenceScope.USER,
    )

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="list_view_preferences",
    )

    organization = models.ForeignKey(
        "core.Organization",
        on_delete=models.CASCADE,
        related_name="list_view_preferences",
    )

    list_type = models.CharField(
        max_length=50,
        choices=ListViewType,
    )

    visible_columns = ArrayField(
        models.CharField(max_length=100),
        help_text=_("Ordered list of visible column names"),
        default=list,
    )

    default_sort = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Default sort field (e.g., '-updated_at')"),
    )

    saved_filters = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Saved filter presets"),
    )

    items_per_page = models.PositiveIntegerField(
        default=25,
        help_text=_("Number of items per page"),
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organization", "list_type"],
                condition=models.Q(scope=PreferenceScope.USER),
                name="unique_user_list_view_preference",
            ),
            models.UniqueConstraint(
                fields=["organization", "list_type"],
                condition=models.Q(scope=PreferenceScope.ORGANIZATION, user__isnull=True),
                name="unique_org_list_view_preference",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(scope=PreferenceScope.USER, user__isnull=False)
                    | models.Q(scope=PreferenceScope.ORGANIZATION, user__isnull=True)
                ),
                name="scope_user_consistency",
            ),
        ]

    def __str__(self) -> str:
        if self.scope == PreferenceScope.USER:
            return f"{self.user} - {self.list_type}"
        return f"{self.organization} (org default) - {self.list_type}"
