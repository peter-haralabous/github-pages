"""HealthSummary model for AI-generated patient health summaries."""

import hashlib
import json

import pghistory
from django.db import models

from sandwich.core.models.abstract import BaseModel
from sandwich.core.models.patient import Patient


class SummaryType(models.TextChoices):
    """Type of health summary."""

    OVERVIEW = "overview", "Overview"
    FOCUSED = "focused", "Focused"
    COMPREHENSIVE = "comprehensive", "Comprehensive"


@pghistory.track()
class HealthSummary(BaseModel):
    """
    AI-generated summary of a patient's health record.
    Cached to avoid redundant LLM calls.
    """

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="health_summaries",
        help_text="Patient this summary is for",
    )

    summary_type = models.CharField(
        max_length=50,
        choices=SummaryType,
        default=SummaryType.OVERVIEW,
        help_text="Type of summary",
    )

    content = models.TextField(
        help_text="The AI-generated summary (markdown or HTML)",
    )

    # Data hash for cache invalidation
    data_hash = models.CharField(
        max_length=64,
        help_text="SHA256 hash of patient data to detect changes",
    )

    # Metadata
    source_record_ids = models.JSONField(
        default=list,
        blank=True,
        help_text="IDs of health records included in this summary",
    )

    model_version = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="LLM model version used to generate this summary",
    )

    tokens_used = models.IntegerField(
        default=0,
        help_text="Token count for cost tracking",
    )

    generation_time_ms = models.IntegerField(
        default=0,
        help_text="Time taken to generate summary in milliseconds",
    )

    is_current = models.BooleanField(
        default=True,
        help_text="Whether this is the current summary for this data hash",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Health Summary"
        verbose_name_plural = "Health Summaries"
        indexes = [
            models.Index(fields=["patient", "-created_at"]),
            models.Index(fields=["patient", "data_hash"]),
        ]

    def __str__(self) -> str:
        """String representation."""
        return f"{self.patient.full_name} - {self.get_summary_type_display()} ({self.created_at.strftime('%Y-%m-%d')})"

    @staticmethod
    def compute_data_hash(patient: Patient) -> str:
        """
        Compute hash of all patient health data.

        Used to detect when data has changed and summary needs regeneration.
        Release 0: Only includes Conditions, Immunizations, and Practitioners.
        """
        # Gather all health records (Release 0: Conditions, Immunizations, Practitioners only)
        data = {
            "conditions": list(patient.condition_set.values_list("id", "updated_at")),
            "immunizations": list(patient.immunization_set.values_list("id", "updated_at")),
            "practitioners": list(patient.practitioner_set.values_list("id", "updated_at")),
        }
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()
