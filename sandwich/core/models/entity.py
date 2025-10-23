import enum

from django.db import models
from django_enum import EnumField

from sandwich.core.models.abstract import BaseModel


class EntityType(enum.Enum):
    PATIENT = "Patient"
    CONDITION = "Condition"
    MEDICATION = "Medication"
    OBSERVATION = "Observation"
    ALLERGY_INTOLERANCE = "AllergyIntolerance"
    IMMUNIZATION = "Immunization"
    PROCEDURE = "Procedure"
    FAMILY_MEMBER = "FamilyMember"


class Entity(BaseModel):
    """
    A node in the knowledge graph (e.g. patient, symptom, drug, place, etc.)
    """

    type: models.Field[EntityType, EntityType] = EnumField(
        EntityType, null=True, blank=True, help_text="Type of the entity in the knowledge graph."
    )
    metadata = models.JSONField(blank=True, null=True, help_text="e.g., FHIR codes, LOINC, etc.")

    class Meta:
        verbose_name = "Entity"
        verbose_name_plural = "Entities"
        constraints = [
            models.UniqueConstraint(
                models.F("metadata__patient_id"),
                name="unique_patient_id_in_metadata",
                condition=(models.Q(metadata__has_key="patient_id") & models.Q(type=EntityType.PATIENT.value)),
            )
        ]

    def __str__(self) -> str:
        if self.metadata and "label" in self.metadata:
            return str(self.metadata["label"])
        if self.metadata and "name" in self.metadata:
            return str(self.metadata["name"])
        return str(self.pk)
