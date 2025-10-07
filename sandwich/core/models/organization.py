import datetime
import logging

import pydantic
from django.db import IntegrityError
from django.db import models
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django_enum import EnumField
from django_pydantic_field import SchemaField
from slugify import slugify

from sandwich.core.models.abstract import BaseModel


class PatientStatus(pydantic.BaseModel):
    value: str
    label: str


class VerificationType(models.TextChoices):
    NONE = "NONE", _("None")
    DATE_OF_BIRTH = "DATE_OF_BIRTH", _("Date of birth")


class OrganizationManager(models.Manager["Organization"]):
    """
    Manager to support natural keys

    https://docs.djangoproject.com/en/stable/topics/serialization/#natural-keys
    """

    def get_by_natural_key(self, slug: str) -> "Organization":
        return self.get(slug=slug)


def is_slug_collision(exc_info: Exception):
    return "Key (slug)=" in exc_info.args[0]


class Organization(BaseModel):  # type: ignore[django-manager-missing] # see docs/typing
    """
    ... companies, institutions, corporations, departments, community groups, ...

    in the Thrive context this is usually our customer

    https://www.hl7.org/fhir/R5/organization.html
    """

    name = models.CharField(max_length=255)

    slug = models.SlugField(max_length=255, unique=True)

    patient_statuses: list[PatientStatus] = SchemaField(schema=list[PatientStatus], default=[])

    verification_type: models.Field[VerificationType, VerificationType] = EnumField(
        VerificationType,
        default=VerificationType.DATE_OF_BIRTH,
    )

    objects = OrganizationManager()

    def __str__(self) -> str:
        return self.slug

    def save(self, *args, **kwargs):
        # Handle automatic slug assignment; we can remove this if we expose the slug in the future
        if not self.slug:
            self.slug = slugify(self.name)

        # Try to save (in a separate transaction to leave the outer transaction in place)
        with transaction.atomic():
            try:
                super().save(*args, **kwargs)
            except IntegrityError as exc_info:
                if not is_slug_collision(exc_info):
                    raise
            else:
                return

        # Didn't work. Try again with a timestamp-based slug
        self.slug = str(int(datetime.datetime.now(tz=datetime.UTC).timestamp()))
        logging.info("Organization slug collision: %s", self.slug)  # no pk yet
        super().save(*args, **kwargs)

    def natural_key(self) -> tuple[object, ...]:
        return (self.slug,)
