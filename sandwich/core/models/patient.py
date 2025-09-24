import logging
import re
from typing import Self

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchQuery
from django.contrib.postgres.search import SearchRank
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.db.models import F

from sandwich.core.models.abstract import BaseModel
from sandwich.core.models.organization import Organization
from sandwich.users.models import User

logger = logging.getLogger(__name__)


class PatientQuerySet(models.QuerySet):
    def search(self, query: str) -> Self:
        if not query:
            return self

        # Sanitize the query to remove problematic characters
        # Remove or replace characters that cause tsquery syntax errors
        sanitized_query = re.sub(r"[^\w\s]", " ", query)

        terms = sanitized_query.split()
        if not terms:
            return self

        # For partial matching, add :* suffix for prefix search
        prefix_terms = [f"{term}:*" for term in terms]

        search_query = SearchQuery(" & ".join(prefix_terms), search_type="raw", config="english")
        return (
            self.filter(search_vector=search_query)
            .annotate(rank=SearchRank(F("search_vector"), search_query))
            .order_by("-rank")
        )


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
    search_vector = SearchVectorField(null=True, blank=True)

    objects = PatientManager()

    class Meta(BaseModel.Meta):
        indexes = [
            GinIndex(fields=["search_vector"]),
        ]

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
