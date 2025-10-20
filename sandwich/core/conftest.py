import pytest
from django.core.files.base import ContentFile

from sandwich.conftest import django_session_fixtures
from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models import Document
from sandwich.core.models import Encounter
from sandwich.core.models import Organization
from sandwich.core.models import Patient
from sandwich.core.models import Task
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.task import TaskStatus


@pytest.fixture
def encounter(organization: Organization, patient: Patient):
    return Encounter.objects.create(patient=patient, organization=organization, status=EncounterStatus.IN_PROGRESS)


@pytest.fixture
def document(patient: Patient, encounter: Encounter) -> Document:
    return Document.objects.create(
        patient=patient,
        encounter=encounter,
        file=ContentFile("Hello World", name="hello_world.txt"),
    )


@pytest.fixture
def task(encounter: Encounter):
    return Task.objects.create(patient=encounter.patient, encounter=encounter, status=TaskStatus.REQUESTED)


@pytest.fixture
def patient_wo_user(organization: Organization) -> Patient:
    return PatientFactory.create(first_name="John", email="patient_wo_user@example.com", organization=organization)


@pytest.fixture
def encounter_wo_user(organization: Organization, patient_wo_user: Patient):
    return Encounter.objects.create(
        patient=patient_wo_user, organization=organization, status=EncounterStatus.IN_PROGRESS
    )


@pytest.fixture
def task_wo_user(encounter_wo_user: Encounter):
    return Task.objects.create(
        patient=encounter_wo_user.patient, encounter=encounter_wo_user, status=TaskStatus.REQUESTED
    )


template_fixture = django_session_fixtures(["template"])
