from django.core.exceptions import ValidationError
from django.db import models
from private_storage.fields import PrivateFileField

from sandwich.core.models.abstract import BaseModel


class Document(BaseModel):
    """
    A document associated with a patient.

    In FHIR, we'd call this a DocumentReference: https://www.hl7.org/fhir/R5/documentreference.html
    """

    # this is DocumentReference.subject in FHIR
    patient = models.ForeignKey("Patient", on_delete=models.CASCADE)

    # this is DocumentReference.context in FHIR
    # it will be null for patient-uploaded documents that weren't collected in response to a practitioner request
    encounter = models.ForeignKey("Encounter", on_delete=models.CASCADE, null=True, blank=True)

    # there probably want to be more metadata fields here
    # - processing state
    # - who uploaded it
    # - what it is about
    # does the document itself
    # - have a title
    # - have an effective date

    file = PrivateFileField(upload_to="documents/")

    def clean(self):
        if self.encounter and self.patient and self.encounter.patient != self.patient:
            msg = "Encounter and patient do not match."
            raise ValidationError(msg)
