"""List view preference models for customizable table views."""

import logging
from typing import TYPE_CHECKING
from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from sandwich.core.models.abstract import BaseModel
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.patient import Patient

if TYPE_CHECKING:
    from sandwich.core.models import Organization
    from sandwich.users.models import User

logger = logging.getLogger(__name__)

DEFAULT_ITEMS_PER_PAGE = 25
DEFAULT_SORT = "-updated_at"


class ListViewType(models.TextChoices):
    """Types of list views that support preferences."""

    ENCOUNTER_LIST = "encounter_list", _("Encounter List")
    PATIENT_LIST = "patient_list", _("Patient List")
    # Future: task_list, etc.

    def get_content_type(self) -> ContentType | None:
        """Get the Django ContentType associated with this list view type."""
        model_map = {
            self.ENCOUNTER_LIST: Encounter,
            self.PATIENT_LIST: Patient,
        }
        return ContentType.objects.get_for_model(model_map[self])

    def get_standard_column_fields(self) -> set[str]:
        fields = {
            self.ENCOUNTER_LIST: {
                "patient__first_name",
                "patient__email",
                "patient__date_of_birth",
                "is_active",
                "created_at",
                "updated_at",
            },
            self.PATIENT_LIST: {
                "first_name",
                "email",
                "date_of_birth",
                "has_active_encounter",
                "created_at",
                "updated_at",
            },
        }
        return fields.get(self, set())

    def get_column_definitions(self) -> list[dict[str, str]]:
        definitions = {
            self.ENCOUNTER_LIST: [
                {"value": "patient__first_name", "label": "Patient Name", "type": "text"},
                {"value": "patient__email", "label": "Email", "type": "text"},
                {"value": "patient__date_of_birth", "label": "Date of Birth", "type": "date"},
                {"value": "is_active", "label": "Active", "type": "boolean"},
                {"value": "status", "label": "Status", "type": "enum"},
                {"value": "created_at", "label": "Created", "type": "date"},
                {"value": "updated_at", "label": "Last Updated", "type": "date"},
            ],
            self.PATIENT_LIST: [
                {"value": "first_name", "label": "Name", "type": "text"},
                {"value": "email", "label": "Email", "type": "text"},
                {"value": "date_of_birth", "label": "Date of Birth", "type": "date"},
                {"value": "has_active_encounter", "label": "Active Encounter", "type": "boolean"},
                {"value": "created_at", "label": "Created", "type": "date"},
                {"value": "updated_at", "label": "Last Updated", "type": "date"},
            ],
        }
        return definitions.get(self, [])

    def get_field_type(self, field_name: str) -> str | None:
        for field_def in self.get_column_definitions():
            if field_def["value"] == field_name:
                return field_def.get("type", "text")
        return None

    def get_field_choices(self, field_name: str) -> list[tuple[str, str]]:
        if self == self.ENCOUNTER_LIST:
            if field_name == "status":
                return [(status.value, str(status.label)) for status in EncounterStatus]
            if field_name == "is_active":
                return [("True", "Active"), ("False", "Archived")]
        return []


class PreferenceScope(models.TextChoices):
    """Scope of the preference - user or organization."""

    USER = "user", _("User")
    ORGANIZATION = "organization", _("Organization")


class ListViewPreferenceQuerySet(models.QuerySet["ListViewPreference"]):
    """Custom QuerySet for ListViewPreference."""

    def for_user(
        self,
        user: "User",
        organization: "Organization",
        list_type: "ListViewType",
    ) -> "ListViewPreference | None":
        return self.filter(
            user=user,
            organization=organization,
            list_type=list_type,
            scope=PreferenceScope.USER,
        ).first()

    def for_organization(
        self,
        organization: "Organization",
        list_type: "ListViewType",
    ) -> "ListViewPreference | None":
        return self.filter(
            organization=organization,
            list_type=list_type,
            scope=PreferenceScope.ORGANIZATION,
            user__isnull=True,
        ).first()


class ListViewPreferenceManager(models.Manager["ListViewPreference"]):
    def get_queryset(self) -> ListViewPreferenceQuerySet:
        return ListViewPreferenceQuerySet(self.model, using=self._db)

    def get_for_user(
        self,
        user: "User",
        organization: "Organization",
        list_type: "ListViewType",
    ) -> "ListViewPreference":
        """
        Get the effective list preference for a user in an organization.

        Priority:
        1. User's personal preference (if exists)
        2. Organization default preference (if exists)
        3. Unsaved preference object with hardcoded defaults

        Always returns a ListViewPreference with all fields populated.
        """
        logger.debug(
            "Fetching list preference",
            extra={
                "user_id": user.id,
                "organization_id": organization.id,
                "list_type": list_type,
            },
        )

        user_pref = self.get_queryset().for_user(user, organization, list_type)
        if user_pref:
            logger.debug(
                "Found user preference",
                extra={
                    "user_id": user.id,
                    "preference_id": user_pref.id,
                },
            )
            return user_pref

        org_pref = self.get_queryset().for_organization(organization, list_type)
        if org_pref:
            logger.debug(
                "Using organization default preference",
                extra={
                    "organization_id": organization.id,
                    "preference_id": org_pref.id,
                },
            )
            return org_pref

        logger.debug(
            "Using hardcoded defaults (no saved preference)",
            extra={
                "user_id": user.id,
                "organization_id": organization.id,
                "list_type": list_type,
            },
        )
        return ListViewPreference.create_default(organization, list_type)


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

    objects = ListViewPreferenceManager()

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

    @classmethod
    def create_default(
        cls,
        organization: "Organization",
        list_type: "ListViewType",
    ) -> "ListViewPreference":
        """
        Create an unsaved ListViewPreference instance with hardcoded defaults.

        This is used as a fallback when no saved preference exists.
        """
        return cls(
            user=None,
            organization=organization,
            list_type=list_type,
            scope=PreferenceScope.ORGANIZATION,
            visible_columns=cls.get_default_columns(list_type),
            default_sort=cls.get_default_sort(list_type),
            saved_filters=cls.get_default_filters(list_type),
            items_per_page=DEFAULT_ITEMS_PER_PAGE,
        )

    @staticmethod
    def get_default_columns(list_type: "ListViewType") -> list[str]:
        definitions = list_type.get_column_definitions()
        if definitions:
            return [d["value"] for d in definitions]
        return sorted(list_type.get_standard_column_fields())

    @staticmethod
    def get_default_sort(list_type: "ListViewType") -> str:
        defaults = {
            ListViewType.ENCOUNTER_LIST: DEFAULT_SORT,
            ListViewType.PATIENT_LIST: DEFAULT_SORT,
        }
        return defaults.get(list_type, DEFAULT_SORT)

    @staticmethod
    def get_default_filters(list_type: "ListViewType") -> dict[str, Any]:
        """Get default filters for a list type."""
        defaults: dict[ListViewType, dict[str, Any]] = {
            ListViewType.ENCOUNTER_LIST: {
                "model_fields": {"is_active": "True"},
            },
        }
        return defaults.get(list_type, {})

    def fill_defaults(self) -> None:
        list_type = ListViewType(self.list_type)
        if not self.default_sort:
            self.default_sort = self.get_default_sort(list_type)
        if not self.visible_columns:
            self.visible_columns = self.get_default_columns(list_type)

    def save_filters(self, filters: dict[str, Any]) -> "ListViewPreference":
        self.saved_filters = filters

        if self.pk:
            self.save(update_fields=["saved_filters", "updated_at"])
            logger.info(
                "Saved filters to preference",
                extra={
                    "preference_id": self.pk,
                    "num_custom_filters": len(filters.get("custom_attributes", {})),
                },
            )
        else:
            logger.debug("Filters updated on unsaved preference instance")

        return self
