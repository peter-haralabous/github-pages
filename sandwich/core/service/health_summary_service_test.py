"""Tests for health_summary_service."""

import pytest

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models import Condition
from sandwich.core.models import HealthSummary
from sandwich.core.models import Immunization
from sandwich.core.models import Practitioner
from sandwich.core.models import SummaryType
from sandwich.core.service.health_summary_service import get_or_generate_health_summary


@pytest.mark.django_db
def test_get_or_generate_health_summary_creates_summary_for_new_patient():
    """Test that a health summary is created for a patient with no existing summary."""
    patient = PatientFactory.create()

    # Add some health data
    Condition.objects.create(patient=patient, name="Hypertension", status="active")
    Immunization.objects.create(patient=patient, name="COVID-19", date="2024-01-15")
    Practitioner.objects.create(patient=patient, name="Dr. Smith")

    # Generate summary
    summary = get_or_generate_health_summary(patient, SummaryType.OVERVIEW)

    # Verify summary was created
    assert summary is not None
    assert summary.patient == patient
    assert summary.summary_type == SummaryType.OVERVIEW
    assert len(summary.content) > 0
    assert summary.data_hash is not None


@pytest.mark.django_db
def test_get_or_generate_health_summary_returns_cached_summary():
    """Test that cached summary is returned when data hasn't changed."""
    patient = PatientFactory.create()

    # Add some health data
    Condition.objects.create(patient=patient, name="Diabetes", status="active")

    # Generate summary first time
    summary1 = get_or_generate_health_summary(patient, SummaryType.OVERVIEW)
    first_created_at = summary1.created_at

    # Generate summary second time (should return cached)
    summary2 = get_or_generate_health_summary(patient, SummaryType.OVERVIEW)

    # Verify it's the same summary
    assert summary1.id == summary2.id
    assert summary2.created_at == first_created_at


@pytest.mark.django_db
def test_get_or_generate_health_summary_regenerates_when_data_changes():
    """Test that a new summary is generated when patient data changes."""
    patient = PatientFactory.create()

    # Add initial data
    Condition.objects.create(patient=patient, name="Asthma", status="active")

    # Generate first summary
    summary1 = get_or_generate_health_summary(patient, SummaryType.OVERVIEW)
    first_hash = summary1.data_hash

    # Add more data (this changes the hash)
    Immunization.objects.create(patient=patient, name="Flu Shot", date="2024-02-01")

    # Generate summary again
    summary2 = get_or_generate_health_summary(patient, SummaryType.OVERVIEW)

    # Verify it's a new summary with different hash
    assert summary1.id != summary2.id
    assert summary2.data_hash != first_hash


@pytest.mark.django_db
def test_get_or_generate_health_summary_handles_empty_data():
    """Test that summary generation works for patient with no health records."""
    patient = PatientFactory.create()

    # Generate summary with no data
    summary = get_or_generate_health_summary(patient, SummaryType.OVERVIEW)

    # Verify summary was created (should handle empty case gracefully)
    assert summary is not None
    assert summary.patient == patient
    assert len(summary.content) > 0  # Should have some default text


@pytest.mark.django_db
def test_compute_data_hash_changes_when_records_change():
    """Test that the data hash changes when health records are modified."""
    patient = PatientFactory.create()

    # Compute initial hash (no records)
    hash1 = HealthSummary.compute_data_hash(patient)

    # Add a condition
    Condition.objects.create(patient=patient, name="Allergies", status="active")
    hash2 = HealthSummary.compute_data_hash(patient)

    # Add an immunization
    Immunization.objects.create(patient=patient, name="Tetanus", date="2024-03-01")
    hash3 = HealthSummary.compute_data_hash(patient)

    # Add a practitioner
    Practitioner.objects.create(patient=patient, name="Dr. Johnson")
    hash4 = HealthSummary.compute_data_hash(patient)

    # All hashes should be different
    assert hash1 != hash2
    assert hash2 != hash3
    assert hash3 != hash4


@pytest.mark.django_db
def test_compute_data_hash_consistent_for_same_data():
    """Test that the same data produces the same hash."""
    patient = PatientFactory.create()

    # Add some data
    Condition.objects.create(patient=patient, name="Hypertension", status="active")
    Immunization.objects.create(patient=patient, name="COVID-19", date="2024-01-15")

    # Compute hash twice
    hash1 = HealthSummary.compute_data_hash(patient)
    hash2 = HealthSummary.compute_data_hash(patient)

    # Should be identical
    assert hash1 == hash2
