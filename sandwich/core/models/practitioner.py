import pghistory
from django.db import models
from django.urls import reverse

from sandwich.core.models.health_record import HealthRecord


@pghistory.track()
class Practitioner(HealthRecord):
    """
    Practitioner covers all individuals who are engaged in the healthcare process and healthcare-related services as
    part of their formal responsibilities.

    Practitioners include (but are not limited to):
    - physicians, dentists, pharmacists
    - physician assistants, nurses, scribes
    - midwives, dietitians, therapists, optometrists, paramedics
    - medical technicians, laboratory scientists, prosthetic technicians, radiographers
    - social workers, professional homecare providers, official volunteers
    - receptionists handling patient registration
    - IT personnel merging or unmerging patient records
    - service animal (e.g., ward assigned dog capable of detecting cancer in patients)
    - a bus driver for a community organization
    - a lawyer acting for a hospital or a patient
    - a person working for a supplier of a healthcare organization

    The Resource SHALL NOT be used for persons involved without a formal responsibility like friends, relatives or
    neighbours.

    https://hl7.org/fhir/R5/practitioner.html
    """

    name = models.CharField(max_length=255)

    def get_absolute_url(self):
        return reverse("patients:practitioner", kwargs={"practitioner_id": self.id})

    def __str__(self) -> str:
        return self.name
