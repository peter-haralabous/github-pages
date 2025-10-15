import uuid

from django.db import models
from django.utils import timezone

from sandwich.core.models.abstract import BaseModel
from sandwich.core.models.document import Document
from sandwich.users.models import User


class SourceTypes(models.TextChoices):
    DOCUMENT = "document", "Document upload"
    TEXT = "text", "Text"
    CONVERSATION = "conversation", "Conversation"
    FORM_SUBMISSION = "form_submission", "Form submission"


class Provenance(BaseModel):
    """
    A record of the source of a specific fact, including the original document,
    page number, and extraction method.
    This model serves as a detailed provenance record for a single Fact instance.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        Document,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="provenances",
        help_text="The document from which this fact was extracted.",
    )
    source_type = models.CharField(
        blank=True,
        default="",
        max_length=50,
        choices=SourceTypes,
        help_text="The type of source, e.g., 'application/pdf', 'conversation'.",
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
                    models.Q(source_type=SourceTypes.TEXT, user__isnull=False)
                    | ~models.Q(source_type=SourceTypes.TEXT)
                ),
                name="user_required_for_text_source",
            )
        ]

    def __str__(self) -> str:
        doc_str = self.document.pk if self.document else "N/A"
        return f"Provenance for (page {self.page}) from {doc_str}"

    @property
    def url(self) -> str | None:
        if self.document and hasattr(self.document, "file"):
            if self.page:
                return f"{self.document.file.url}#page={self.page}"
            return self.document.file.url
        return None
