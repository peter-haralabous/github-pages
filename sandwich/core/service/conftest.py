from typing import cast

import pytest

from sandwich.core.factories import PatientFactory
from sandwich.core.models import Encounter
from sandwich.core.models import Organization
from sandwich.core.models import Patient
from sandwich.core.models import Task
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.task import TaskStatus


@pytest.fixture
def organization():
    return Organization.objects.create(name="Test Organization")


@pytest.fixture
def patient(organization: Organization) -> Patient:
    return cast(
        "Patient",
        PatientFactory(first_name="John", last_name="Doe", email="jdoe@example.com", organization=organization),
    )


@pytest.fixture
def encounter(organization: Organization, patient: Patient):
    return Encounter.objects.create(patient=patient, organization=organization, status=EncounterStatus.IN_PROGRESS)


@pytest.fixture
def task(encounter: Encounter):
    return Task.objects.create(patient=encounter.patient, encounter=encounter, status=TaskStatus.REQUESTED)
