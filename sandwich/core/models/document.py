import pghistory
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_enum import EnumField
from private_storage.fields import PrivateFileField

from sandwich.core.models.health_record import HealthRecord


class DocumentManager(models.Manager["Document"]):
    def create(self, **kwargs) -> "Document":
        from sandwich.core.service.document_service import assign_default_document_permissions  # noqa: PLC0415

        document = super().create(**kwargs)
        assign_default_document_permissions(document)
        return document


class DocumentCategory(models.TextChoices):
    LAB_RESULTS = "lab_results", _("Lab Results")
    HEALTH_VISITS = "health_visits", _("Health Visits")
    HOSPITAL_VISITS = "hospital_visits", _("Hospital Visits")
    IMMUNIZATIONS = "immunizations", _("Immunizations")
    PRESCRIPTIONS = "prescriptions", _("Prescriptions")
    MY_NOTES = "my_notes", _("My Notes")
    FAMILY_HISTORY = "family_history", _("Family History")
    OTHER = "other", _("Other")


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

    # metadata extracted from the file's content
    date = models.DateField(null=True, blank=True)
    category: models.Field[DocumentCategory, DocumentCategory] = EnumField(
        DocumentCategory, default=DocumentCategory.OTHER
    )

    objects = DocumentManager()

    def get_absolute_url(self):
        return reverse("patients:document", kwargs={"document_id": self.id})

    def __str__(self):
        return self.original_filename
