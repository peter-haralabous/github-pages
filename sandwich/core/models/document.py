import pghistory
from django.db import models
from private_storage.fields import PrivateFileField

from sandwich.core.models.health_record import HealthRecord


class DocumentManager(models.Manager["Document"]):
    def create(self, **kwargs) -> "Document":
        from sandwich.core.service.document_service import assign_default_document_permissions  # noqa: PLC0415

        document = super().create(**kwargs)
        assign_default_document_permissions(document)
        return document


@pghistory.track()
class Document(HealthRecord):
    """
    A document associated with a patient.

    In FHIR, we'd call this a DocumentReference: https://www.hl7.org/fhir/R5/documentreference.html
    """

    # there probably want to be more metadata fields here
    # - processing state
    # - who uploaded it
    # - what it is about
    # does the document itself
    # - have a title
    # - have an effective date

    file = PrivateFileField(upload_to="documents/")

    # metadata about the uploaded file
    content_type = models.CharField(max_length=255, blank=True)
    size = models.BigIntegerField(null=True, blank=True)
    original_filename = models.CharField(max_length=255, blank=True)

    objects = DocumentManager()
