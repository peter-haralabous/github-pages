import pydantic
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_enum import EnumField
from django_pydantic_field import SchemaField

from sandwich.core.models.abstract import BaseModel


class PatientStatus(pydantic.BaseModel):
    value: str
    label: str


class VerificationType(models.TextChoices):
    NONE = "NONE", _("None")
    DATE_OF_BIRTH = "DATE_OF_BIRTH", _("Date of birth")


class Organization(BaseModel):  # type: ignore[django-manager-missing] # see docs/typing
    """
    ... companies, institutions, corporations, departments, community groups, ...

    in the Thrive context this is usually our customer

    https://www.hl7.org/fhir/R5/organization.html
    """

    name = models.CharField(max_length=255)

    patient_statuses: list[PatientStatus] = SchemaField(schema=list[PatientStatus], default=[])

    verification_type: models.Field[VerificationType, VerificationType] = EnumField(
        VerificationType,
        default=VerificationType.DATE_OF_BIRTH,
    )
