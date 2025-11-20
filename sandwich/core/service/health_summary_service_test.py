import pytest

from sandwich.core.models import Condition
from sandwich.core.models import Immunization
from sandwich.core.models import Patient
from sandwich.core.models import Practitioner
from sandwich.core.models.condition import ConditionStatus
from sandwich.core.service.health_summary_service import generate_health_summary


@pytest.fixture
def basic_patient(db):
    """Create a basic patient with fixed UUID."""
    return Patient.objects.create(
        id="00000000-0000-0000-0000-000000000001",
        first_name="John",
        last_name="Doe",
        date_of_birth="1990-01-01",
    )


@pytest.fixture
def patient_with_conditions(db):
    """Create a patient with conditions using fixed UUIDs."""
    patient = Patient.objects.create(
        id="00000000-0000-0000-0000-000000000002",
        first_name="Jane",
        last_name="Smith",
        date_of_birth="1985-05-15",
    )
    Condition.objects.create(
        id="00000000-0000-0000-0000-000000000101",
        patient=patient,
        name="Type 2 Diabetes",
        status=ConditionStatus.ACTIVE,
        onset="2020-01-15",
    )
    Condition.objects.create(
        id="00000000-0000-0000-0000-000000000102",
        patient=patient,
        name="Hypertension",
        status=ConditionStatus.ACTIVE,
        onset="2019-06-01",
    )
    return patient


@pytest.fixture
def patient_with_immunizations(db):
    """Create a patient with immunizations using fixed UUIDs."""
    patient = Patient.objects.create(
        id="00000000-0000-0000-0000-000000000003",
        first_name="Alice",
        last_name="Johnson",
        date_of_birth="1992-03-20",
    )
    Immunization.objects.create(
        id="00000000-0000-0000-0000-000000000201",
        patient=patient,
        name="COVID-19 Vaccine",
        date="2023-03-15",
    )
    Immunization.objects.create(
        id="00000000-0000-0000-0000-000000000202",
        patient=patient,
        name="Influenza Vaccine",
        date="2023-10-01",
    )
    return patient


@pytest.fixture
def patient_with_practitioners(db):
    """Create a patient with care team using fixed UUIDs."""
    patient = Patient.objects.create(
        id="00000000-0000-0000-0000-000000000004",
        first_name="Bob",
        last_name="Williams",
        date_of_birth="1978-11-30",
    )
    Practitioner.objects.create(
        id="00000000-0000-0000-0000-000000000301",
        patient=patient,
        name="Dr. Sarah Chen",
    )
    Practitioner.objects.create(
        id="00000000-0000-0000-0000-000000000302",
        patient=patient,
        name="Dr. Michael Rodriguez",
    )
    return patient


@pytest.mark.vcr
@pytest.mark.django_db
def test_generate_health_summary_basic(basic_patient):
    """Test that generate_health_summary returns markdown content for a basic patient."""
    summary = generate_health_summary(basic_patient)

    assert isinstance(summary, str)
    assert len(summary) > 0
    # Should be markdown formatted
    assert any(char in summary for char in ["#", "*", "-"])


@pytest.mark.vcr
@pytest.mark.django_db
def test_generate_health_summary_with_conditions(patient_with_conditions):
    """Test health summary generation for a patient with medical conditions."""
    summary = generate_health_summary(patient_with_conditions)

    assert isinstance(summary, str)
    assert len(summary) > 0


@pytest.mark.vcr
@pytest.mark.django_db
def test_generate_health_summary_with_immunizations(patient_with_immunizations):
    """Test health summary generation for a patient with immunization records."""
    summary = generate_health_summary(patient_with_immunizations)

    assert isinstance(summary, str)
    assert len(summary) > 0


@pytest.mark.vcr
@pytest.mark.django_db
def test_generate_health_summary_with_practitioners(patient_with_practitioners):
    """Test health summary generation for a patient with care team members."""
    summary = generate_health_summary(patient_with_practitioners)

    assert isinstance(summary, str)
    assert len(summary) > 0
