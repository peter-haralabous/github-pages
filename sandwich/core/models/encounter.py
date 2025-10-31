from typing import Self

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.search import SearchRank
from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from django_enum import EnumField

from sandwich.core.models.abstract import BaseModel
from sandwich.core.models.custom_attribute import CustomAttributeValue
from sandwich.core.models.organization import Organization
from sandwich.core.models.patient import Patient
from sandwich.core.models.patient import to_search_query


class EncounterStatus(models.TextChoices):
    """
    https://www.hl7.org/fhir/R5/valueset-encounter-status.html
    """

    # These are more options than we want to expose in the UI, but we'll want at least a couple.
    # Don't add new ones! This comes from the FHIR spec.
    PLANNED = "planned", _("Planned")
    IN_PROGRESS = "in-progress", _("In Progress")
    ON_HOLD = "on-hold", _("On Hold")
    DISCHARGED = "discharged", _("Discharged")
    COMPLETED = "completed", _("Completed")
    CANCELLED = "cancelled", _("Cancelled")
    DISCONTINUED = "discontinued", _("Discontinued")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    UNKNOWN = "unknown", _("Unknown")


def terminal_encounter_status(status: EncounterStatus) -> bool:
    return status in [
        EncounterStatus.CANCELLED,
        EncounterStatus.COMPLETED,
        EncounterStatus.DISCHARGED,
        EncounterStatus.DISCONTINUED,
        EncounterStatus.ENTERED_IN_ERROR,
    ]


class EncounterQuerySet(models.QuerySet):
    def search(self, query: str) -> Self:
        search_query = to_search_query(query)
        if not search_query:
            return self

        return (
            self.filter(patient__search_vector=search_query)
            .annotate(rank=SearchRank(F("patient__search_vector"), search_query))
            .order_by("-rank")
        )


class EncounterManager(models.Manager["Encounter"]):
    def get_queryset(self):
        return EncounterQuerySet(self.model, using=self._db)

    def search(self, query: str):
        return self.get_queryset().search(query)

    def create(self, **kwargs) -> "Encounter":
        from sandwich.core.service.encounter_service import assign_default_encounter_perms  # noqa: PLC0415

        created = super().create(**kwargs)
        assign_default_encounter_perms(created)
        return created


class Encounter(BaseModel):
    """
    An interaction between a patient and healthcare provider(s) for the purpose of providing healthcare service(s) or
    assessing the health status of a patient.

    https://www.hl7.org/fhir/R5/encounter.html
    """

    # this is Encounter.serviceProvider in FHIR
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    # this is Encounter.subject in FHIR
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    # This is _not_ a client-extensible ValueSet; we'll want a second field to hold custom statuses that they define.
    # in the Jira model, this is "Resolution"; "Status" is below
    status: models.Field[EncounterStatus, EncounterStatus] = EnumField(EncounterStatus)

    # this is Encounter.actualPeriod.end in FHIR
    ended_at = models.DateTimeField(blank=True, null=True)

    # User defined custom attributes (EAV model)
    attributes = GenericRelation(
        CustomAttributeValue,
        related_query_name="encounter",
    )

    objects = EncounterManager()

    @property
    def name(self):
        return f"Encounter {self.id}"

    @property
    def active(self) -> bool:
        return not terminal_encounter_status(self.status)
