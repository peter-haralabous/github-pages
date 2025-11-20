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
def other_user(db) -> User:
    return UserFactory.create(consents=ConsentMiddleware.required_policies)


@pytest.fixture
def other_organization(db) -> Organization:
    return OrganizationFactory.create(name="Other Organization")


@pytest.fixture
def other_patient(other_organization: Organization, other_user: User) -> Patient:
    """
    Creates a user-owned patient
    """
    patient = PatientFactory.create(
        first_name="John", last_name="Doe", email="jdoe@example.com", organization=other_organization, user=other_user
    )
    patient.assign_user_owner_perms(other_user)
    return patient


@pytest.fixture
def other_provider(db, other_organization: Organization) -> User:
    return UserFactory.create(
        email="provider@other.organization.org",
        consents=ConsentMiddleware.required_policies,
        groups={role.group for role in other_organization.role_set.filter(name=RoleName.STAFF)},
    )


@pytest.fixture
def other_owner(db, other_organization: Organization) -> User:
    return UserFactory.create(
        email="owner@other.organization.org",
        consents=ConsentMiddleware.required_policies,
        groups={role.group for role in other_organization.role_set.filter(name=RoleName.OWNER)},
    )


@pytest.fixture
def other_condition(other_patient: Patient, other_encounter: Encounter) -> Condition:
    return ConditionFactory.create(patient=other_patient, encounter=other_encounter)


@pytest.fixture
def other_document(other_patient: Patient, other_encounter: Encounter) -> Document:
    return Document.objects.create(
        patient=other_patient,
        encounter=other_encounter,
        file=ContentFile("Hello World", name="hello_world.txt"),
    )


@pytest.fixture
def other_encounter(other_patient, other_organization):
    return EncounterFactory.create(patient=other_patient, organization=other_organization)


@pytest.fixture
def other_task(other_encounter: Encounter):
    return Task.objects.create(patient=other_encounter.patient, encounter=other_encounter, status=TaskStatus.REQUESTED)
