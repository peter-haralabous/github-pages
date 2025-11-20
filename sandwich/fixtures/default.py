import pytest
from django.core.files.base import ContentFile

from sandwich.core.factories.condition import ConditionFactory
from sandwich.core.factories.encounter import EncounterFactory
from sandwich.core.factories.organization import OrganizationFactory
from sandwich.core.factories.patient import PatientFactory
from sandwich.core.middleware import ConsentMiddleware
from sandwich.core.models import Condition
from sandwich.core.models import Document
from sandwich.core.models import Encounter
from sandwich.core.models import Organization
from sandwich.core.models import Patient
from sandwich.core.models import Task
from sandwich.core.models.role import RoleName
from sandwich.core.models.task import TaskStatus
from sandwich.users.factories import UserFactory
from sandwich.users.models import User


@pytest.fixture
def user(db) -> User:
    return UserFactory.create(consents=ConsentMiddleware.required_policies)


@pytest.fixture
def organization(db) -> Organization:
    return OrganizationFactory.create(name="Test Organization")


@pytest.fixture
def patient(organization: Organization, user: User) -> Patient:
    """
    Creates a user-owned patient
    """
    patient = PatientFactory.create(
        first_name="John", last_name="Doe", email="jdoe@example.com", organization=organization, user=user
    )
    patient.assign_user_owner_perms(user)
    return patient


@pytest.fixture
def provider(db, organization: Organization) -> User:
    return UserFactory.create(
        email="provider@organization.org",
        consents=ConsentMiddleware.required_policies,
        groups={role.group for role in organization.role_set.filter(name=RoleName.STAFF)},
    )


@pytest.fixture
def owner(db, organization: Organization) -> User:
    return UserFactory.create(
        email="owner@organization.org",
        consents=ConsentMiddleware.required_policies,
        groups={role.group for role in organization.role_set.filter(name=RoleName.OWNER)},
    )


@pytest.fixture
def condition(patient: Patient, encounter: Encounter) -> Condition:
    return ConditionFactory.create(patient=patient, encounter=encounter)


@pytest.fixture
def document(patient: Patient, encounter: Encounter) -> Document:
    return Document.objects.create(
        patient=patient,
        encounter=encounter,
        file=ContentFile("Hello World", name="hello_world.txt"),
    )


@pytest.fixture
def encounter(patient, organization):
    return EncounterFactory.create(patient=patient, organization=organization)


@pytest.fixture
def task(encounter: Encounter):
    return Task.objects.create(patient=encounter.patient, encounter=encounter, status=TaskStatus.REQUESTED)
