import logging
from typing import Self

from django.db import models
from django.db.models.expressions import RawSQL

from sandwich.core.models.abstract import BaseModel
from sandwich.core.models.organization import Organization
from sandwich.users.models import User

logger = logging.getLogger(__name__)


def escape_fts5(query: str) -> str:
    # TODO: we could do a lot better here
    def quote(s: str) -> str:
        return f'"{s.replace('"', '""')}"*'

    return " AND ".join(quote(t.strip()) for t in query.split())


class PatientQuerySet(models.QuerySet):
    def search(self, query: str) -> Self:
        """
        Performs a full-text search and filters the current QuerySet.
        """
        if not query:
            return self

        query = escape_fts5(query)

        # important note: the subquery isn't executed eagerly; it'll be evaluated later
        # when the whole QuerySet is fetched.
        subquery = "SELECT patient_uuid FROM core_patient_fts WHERE core_patient_fts MATCH %s"

        return self.filter(pk__in=RawSQL(subquery, [query]))  # noqa: S611


class PatientManager(models.Manager["Patient"]):
    def get_queryset(self):
        return PatientQuerySet(self.model, using=self._db)

    # You can keep the search method on the manager if you want to be
    # able to call Patient.objects.search() directly as a shortcut.
    def search(self, query: str):
        return self.get_queryset().search(query)


class Patient(BaseModel):
    """
    Administrative information about an individual receiving care

    https://hl7.org/fhir/R5/patient.html
    """

    # TODO: keep this in sync with the "owning" user's profile?
    #       this is the email that a practitioner set when sending the first message to a patient
    #       once the user has claimed their Patient we shouldn't be using it anymore
    email = models.EmailField(blank=True)

    date_of_birth = models.DateField(blank=True, null=True)

    # TODO: name modelled incorrectly but expediently
    #       this is how we think about patients in BC, but it's definitely not universal
    #       see https://www.kalzumeus.com/2010/06/17/falsehoods-programmers-believe-about-names/
    #       and https://hl7.org/fhir/R5/datatypes.html#HumanName
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    # TODO: patients may have multiple identifiers, not just a BC PHN
    #       i.e. this is implicitly system=https://fhir.infoway-inforoute.ca/NamingSystem/ca-bc-patient-healthcare-id
    #       see https://simplifier.net/canadianuriregistry/~resources?category=NamingSystem&sortBy=LastUpdateDate_desc
    phn = models.CharField(max_length=255, verbose_name="Personal health number", blank=True)

    # a user can have many patients. in the future we may allow multiple users to manage care of a single patient.
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    # each patient record belongs to at most one organization
    # TODO: pull in patient merging logic from Classic
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)

    objects = PatientManager()

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
