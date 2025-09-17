import pydantic
from django.db import models
from django_pydantic_field import SchemaField

from sandwich.core.models.abstract import TimestampedModel


class PatientStatus(pydantic.BaseModel):
    value: str
    label: str


class Organization(TimestampedModel):
    """
    ... companies, institutions, corporations, departments, community groups, ...

    in the Thrive context this is usually our customer

    https://www.hl7.org/fhir/R5/organization.html
    """

    name = models.CharField(max_length=255)

    patient_statuses: list[PatientStatus] = SchemaField(schema=list[PatientStatus], default=[])
