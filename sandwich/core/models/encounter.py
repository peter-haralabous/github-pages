from django.db import models
from django.utils.translation import gettext_lazy as _
from django_enum import EnumField

from sandwich.core.models.abstract import TimestampedModel
from sandwich.core.models.organization import Organization
from sandwich.core.models.patient import Patient


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


class Encounter(TimestampedModel):
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

    # this is Encounter.subjectStatus in FHIR (https://www.hl7.org/fhir/R5/encounter.html#8.11.1.1)
    # we can use a client-defined ontology for these statuses
    patient_status = models.CharField(max_length=255, blank=True)

    # this is Encounter.actualPeriod.end om FHIR
    ended_at = models.DateTimeField(blank=True, null=True)

    @property
    def name(self):
        return f"Encounter {self.id}"

    @property
    def active(self) -> bool:
        return not terminal_encounter_status(self.status)

    def get_patient_status_display(self) -> str:
        # NOTE-NG: the name of this method matches the magic one that Django would normally generate
        # https://docs.djangoproject.com/en/5.2/ref/models/instances/#django.db.models.Model.get_FOO_display
        if self.patient_status:
            for option in self.organization.patient_statuses:
                if option.value == self.patient_status:
                    return option.label
        return self.patient_status
