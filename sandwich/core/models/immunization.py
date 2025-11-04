import pghistory
from django.db import models

from sandwich.core.models.health_record import HealthRecord


@pghistory.track()
class Immunization(HealthRecord):
    """
    Describes the event of a patient being administered a vaccine or a record of an immunization as reported by
    a patient, a clinician or another party.

    https://www.hl7.org/fhir/R5/immunization.html
    """

    # this is Immunization.occurrence in FHIR
    # TODO: introduce a mixed-precision date field that accepts all of {2000,2000-01,2000-01-01,2000-01-01T00:00:00}
    date = models.DateField()

    name = models.CharField(max_length=255)

    # # this is Immunization.vaccineCode.coding[0].display in FHIR
    # vaccine_display = models.CharField(max_length=255, blank=True)
    # # this is Immunization.vaccineCode.coding[0].code in FHIR
    # vaccine_code = models.CharField(max_length=255, blank=True)
    # # this is Immunization.protocolApplied.targetDisease in FHIR
    # target_disease = models.CharField(max_length=255, blank=True)
