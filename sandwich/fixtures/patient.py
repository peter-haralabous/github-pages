import pytest

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models import Organization
from sandwich.core.models import Patient
from sandwich.users.models import User


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
