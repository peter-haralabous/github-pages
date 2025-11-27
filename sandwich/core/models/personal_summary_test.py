from datetime import timedelta
from typing import Any

from django.utils import timezone

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.factories.personal_summary import PersonalSummaryFactory
from sandwich.core.models import Patient
from sandwich.core.models.personal_summary import PersonalSummary
from sandwich.core.models.personal_summary import PersonalSummaryType


def test_get_most_recent_summary_returns_none_when_no_summaries(db: Any, patient: Patient) -> None:
    assert PersonalSummary.objects.get_most_recent_summary(patient) is None


def test_get_most_recent_summary_returns_recent_summary(db: Any, patient: Patient) -> None:
    """Ensure it returns the most recent health summary for the target patient.

    Doesn't return summaries for other patients, and returns the most recent if multiple exist.
    """
    # Create summary for patient2 to ensure filtering works
    patient2 = PatientFactory.create()
    PersonalSummaryFactory.create(
        patient=patient2,
    )

    older_summary = PersonalSummaryFactory.create(patient=patient)

    # Manually set it to 10 hours ago
    older_created_at = timezone.now() - timedelta(hours=10)
    PersonalSummary.objects.filter(id=older_summary.id).update(created_at=older_created_at)

    # Create newer summary (5 hours ago)
    newer_summary = PersonalSummaryFactory.create(patient=patient)
    newer_created_at = timezone.now() - timedelta(hours=5)
    PersonalSummary.objects.filter(id=newer_summary.id).update(created_at=newer_created_at)

    result = PersonalSummary.objects.get_most_recent_summary(patient)
    assert result is not None
    assert result.id == newer_summary.id
    assert result.summary_type == PersonalSummaryType.HEALTH_SUMMARY
    assert result.patient == patient
