import pytest

from sandwich.conftest import django_session_fixtures
from sandwich.core.factories import PatientFactory
from sandwich.core.models import Encounter
from sandwich.core.models import Organization
from sandwich.core.models import Patient
from sandwich.core.models import Task
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.task import TaskStatus
from sandwich.users.factories import UserFactory
from sandwich.users.models import User


@pytest.fixture
def user_wo_consent(db) -> User:
    return UserFactory.create(consent=None)


@pytest.fixture
def organization():
    return Organization.objects.create(name="Test Organization")


@pytest.fixture
def patient(organization: Organization) -> Patient:
    return PatientFactory.create(
        first_name="John", last_name="Doe", email="jdoe@example.com", organization=organization
    )


@pytest.fixture
def encounter(organization: Organization, patient: Patient):
    return Encounter.objects.create(patient=patient, organization=organization, status=EncounterStatus.IN_PROGRESS)


@pytest.fixture
def task(encounter: Encounter):
    return Task.objects.create(patient=encounter.patient, encounter=encounter, status=TaskStatus.REQUESTED)


template_fixture = django_session_fixtures(["template"])
