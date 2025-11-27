from datetime import timedelta
from typing import Any

from django.utils import timezone
from freezegun import freeze_time

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.factories.personal_summary import PersonalSummaryFactory
from sandwich.core.models import Patient
from sandwich.core.models.personal_summary import PersonalSummary
from sandwich.core.models.personal_summary import PersonalSummaryType


def test_get_most_recent_health_summary_returns_none_when_no_summaries(db: Any, patient: Patient) -> None:
    result = PersonalSummary.objects.get_most_recent_health_summary_in_last_24hrs(patient)
    assert result is None


def test_get_most_recent_health_summary_returns_recent_summary(db: Any, patient: Patient) -> None:
    """Test that the method returns a health summary created within the last 24 hours."""
    # Create summary for patient2 to ensure filtering works
    patient2 = PatientFactory.create()
    PersonalSummaryFactory.create(
        patient=patient2,
    )

    summary = PersonalSummaryFactory.create(
        patient=patient,
    )
    result = PersonalSummary.objects.get_most_recent_health_summary_in_last_24hrs(patient)
    assert result is not None
    assert result.id == summary.id
    assert result.summary_type == PersonalSummaryType.HEALTH_SUMMARY
    assert result.patient == patient


def test_get_most_recent_health_summary_excludes_old_summaries(db: Any, patient: Patient) -> None:
    """Test that the method excludes health summaries older than 24 hours."""
    old_summary = PersonalSummaryFactory.create(
        patient=patient,
    )

    # Manually set created_at to 25 hours ago (outside 24-hour window)
    old_created_at = timezone.now() - timedelta(hours=25)
    PersonalSummary.objects.filter(id=old_summary.id).update(created_at=old_created_at)

    result = PersonalSummary.objects.get_most_recent_health_summary_in_last_24hrs(patient)
    assert result is None


def test_get_most_recent_health_summary_returns_most_recent_when_multiple(db: Any, patient: Patient) -> None:
    """Test that the method returns the most recent summary when multiple exist within 24 hours."""
    # Create first summary
    older_summary = PersonalSummaryFactory.create(patient=patient)

    # Manually set it to 10 hours ago
    older_created_at = timezone.now() - timedelta(hours=10)
    PersonalSummary.objects.filter(id=older_summary.id).update(created_at=older_created_at)

    # Create newer summary (5 hours ago)
    newer_summary = PersonalSummaryFactory.create(patient=patient)
    newer_created_at = timezone.now() - timedelta(hours=5)
    PersonalSummary.objects.filter(id=newer_summary.id).update(created_at=newer_created_at)

    result = PersonalSummary.objects.get_most_recent_health_summary_in_last_24hrs(patient)
    assert result is not None
    assert result.id == newer_summary.id


def test_get_most_recent_health_summary_boundary_case_exactly_24_hours(db: Any, patient: Patient) -> None:
    """Test that a summary created exactly 24 hours ago is included."""
    summary = PersonalSummaryFactory.create(patient=patient)

    # Set created_at to exactly 24 hours ago
    exact_cutoff = timezone.now() - timedelta(hours=24)
    with freeze_time(exact_cutoff):
        PersonalSummary.objects.filter(id=summary.id).update(created_at=exact_cutoff)

        result = PersonalSummary.objects.get_most_recent_health_summary_in_last_24hrs(patient)
    assert result is not None
    assert result.id == summary.id
