import enum

from django.db import models
from django_enum import EnumField

from sandwich.core.models.abstract import BaseModel


class PredicateName(enum.Enum):
    HAS_CONDITION = "HAS_CONDITION"
    TAKES_MEDICATION = "TAKES_MEDICATION"
    HAS_LAB_RESULT = "HAS_LAB_RESULT"
    HAS_VITAL_SIGN = "HAS_VITAL_SIGN"
    HAS_SYMPTOM = "HAS_SYMPTOM"
    HAS_ALLERGY = "HAS_ALLERGY"
    HAS_FAMILY_HISTORY = "HAS_FAMILY_HISTORY"
    RECEIVED_IMMUNIZATION = "RECEIVED_IMMUNIZATION"
    UNDERWENT_PROCEDURE = "UNDERWENT_PROCEDURE"


class Predicate(BaseModel):
    """
    A named relationship between two entities (e.g. 'HAS_CONDITION', 'TAKES_MEDICATION', etc.)
    """

    name: models.Field[PredicateName, PredicateName] = EnumField(
        PredicateName, help_text="Predicate name (relationship type between entities)."
    )
    description = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name.value
