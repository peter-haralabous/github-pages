from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_enum import EnumField

from sandwich.core.models.abstract import BaseModel
from sandwich.core.models.document import Document
from sandwich.users.models import User


class SourceType(models.TextChoices):
    DOCUMENT = "document", _("Document upload")
    TEXT = "text", _("Text")
    UNKNOWN = "unknown", _("Unknown")

    # these are planned, but not yet implemented
    # when adding them, also add a ForeignKey to the appropriate model
    # CONVERSATION = "conversation", _("Conversation")
    # FORM_SUBMISSION = "form_submission", _("Form submission")


class Provenance(BaseModel):
    """
    A record of the source of a specific fact, including the original document,
    page number, and extraction method.
    This model serves as a detailed provenance record for a single Fact instance.
    """

    document = models.ForeignKey(
        Document,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="provenances",
        help_text="The document from which this fact was extracted.",
    )
    source_type: models.Field[SourceType, SourceType] = EnumField(
        SourceType,
        default=SourceType.UNKNOWN,
    )
    page = models.IntegerField(
        null=True,
        blank=True,
        help_text="The page number from which the fact was extracted (if applicable).",
    )
    extracted_at = models.DateTimeField(default=timezone.now, help_text="The timestamp when the fact was extracted.")
    extracted_by = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="The name of the tool or LLM used for extraction.",
    )
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="The user who created the text, if source_type is TEXT.",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(source_type=SourceType.TEXT, user__isnull=False) | ~models.Q(source_type=SourceType.TEXT)
                ),
                name="user_required_for_text_source",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(source_type=SourceType.DOCUMENT, document__isnull=False)
                    | ~models.Q(source_type=SourceType.DOCUMENT)
                ),
                name="document_required_for_document_source",
            ),
        ]

    def __str__(self) -> str:
        doc_str = self.document.pk if self.document else "N/A"
        return f"Provenance for (page {self.page}) from {doc_str}"

    @property
    def patient_url(self) -> str | None:
        if self.document and hasattr(self.document, "file"):
            fragment = f"page={self.page}" if self.page else None
            return reverse("patients:document_download", kwargs={"document_id": self.document.id}, fragment=fragment)
        return None
