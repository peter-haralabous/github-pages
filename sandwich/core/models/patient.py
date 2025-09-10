from django.db import models

from sandwich.core.models.abstract import TimestampedModel
from sandwich.core.models.organization import Organization
from sandwich.users.models import User


class Patient(TimestampedModel):
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
