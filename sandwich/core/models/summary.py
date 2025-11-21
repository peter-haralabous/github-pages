from django.db import models
from django.utils.translation import gettext_lazy as _
from django_enum import EnumField

from sandwich.core.models.abstract import BaseModel
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.form_submission import FormSubmission
from sandwich.core.models.organization import Organization
from sandwich.core.models.patient import Patient
from sandwich.core.models.summary_template import SummaryTemplate


class SummaryStatus(models.TextChoices):
    PENDING = "pending", _("Pending")
    PROCESSING = "processing", _("Processing")
    SUCCEEDED = "succeeded", _("Succeeded")
    FAILED = "failed", _("Failed")


class SummaryManager(models.Manager["Summary"]):
    def create(self, **kwargs) -> "Summary":
        from sandwich.core.service.summary_service import assign_default_summary_perms  # noqa: PLC0415

        created = super().create(**kwargs)
        assign_default_summary_perms(created)
        return created


class Summary(BaseModel):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, help_text="Patient this summary is about")

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, help_text="Organization for access control"
    )

    encounter = models.ForeignKey(
        Encounter,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Optional encounter context for this summary",
    )

    template = models.ForeignKey(
        SummaryTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Template used to generate this summary",
    )

    submission = models.ForeignKey(
        FormSubmission,
        on_delete=models.CASCADE,
        help_text="Form submission being summarized",
    )

    title = models.CharField(max_length=255, help_text="Title of the summary (usually from template name)")
    body = models.TextField(blank=True, help_text="Generated markdown/HTML content")
    status: models.Field[SummaryStatus, SummaryStatus] = EnumField(
        SummaryStatus, default=SummaryStatus.PENDING, help_text="Current generation status"
    )

    objects = SummaryManager()

    class Meta:
        verbose_name_plural = "Summaries"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} - {self.patient.full_name} ({self.get_status_display()})"

    @property
    def is_complete(self) -> bool:
        """Whether summary generation is complete (succeeded or failed)."""
        return self.status in [SummaryStatus.SUCCEEDED, SummaryStatus.FAILED]
