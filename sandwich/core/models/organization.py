from django.db import models

from sandwich.core.models.abstract import TimestampedModel


class Organization(TimestampedModel):
    """
    ... companies, institutions, corporations, departments, community groups, ...

    in the Thrive context this is usually our customer

    https://www.hl7.org/fhir/R5/organization.html
    """

    name = models.CharField(max_length=255)

    # TODO: organization defines the patient statuses that the want to use. how do we manage this?
    #       a CSV string field here? feels wrong
    #       JSON-formatted { value, label } pairs? maybe
    #       another Django model? maybe
    # patient_statuses = models.CharField(max_length=255, blank=True)
