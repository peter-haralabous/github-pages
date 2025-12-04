import pghistory
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_enum import EnumField

from sandwich.core.models.health_record import HealthRecord


class ConditionStatus(models.TextChoices):
    """
    https://hl7.org/fhir/R5/valueset-condition-clinical.html
    """

    ACTIVE = "active", _("Active")
    RECURRENCE = "recurrence", _("Recurrence")
    RELAPSE = "relapse", _("Relapse")
    INACTIVE = "inactive", _("Inactive")
    REMISSION = "remission", _("Remission")
    RESOLVED = "resolved", _("Resolved")
    UNKNOWN = "unknown", _("Unknown")


@pghistory.track()
class Condition(HealthRecord):
    """
    A clinical condition, problem, diagnosis, or other event, situation, issue, or clinical concept that has risen to a
    level of concern.

    https://hl7.org/fhir/R5/condition.html
    """

    # name alone is a very simplistic way to describe the condition
    # in FHIR we might use https://hl7.org/fhir/R5/valueset-condition-code.html
    name = models.CharField(max_length=255)

    # these three fields come from the FHIR spec
    status: models.Field[ConditionStatus, ConditionStatus] = EnumField(
        ConditionStatus, default=ConditionStatus.UNKNOWN
    )
    # to be consistent with other models we might want to rename these to start_date and end_date
    onset = models.DateField(null=True, blank=True)
    abatement = models.DateField(null=True, blank=True)

    def get_absolute_url(self) -> str:
        return reverse("patients:condition", kwargs={"condition_id": self.id})

    def __str__(self):
        return self.name
