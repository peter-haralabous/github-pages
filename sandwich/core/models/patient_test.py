import pytest

from sandwich.core.factories.organization import OrganizationFactory
from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models import Organization
from sandwich.core.models import Patient
from sandwich.users.models import User


@pytest.mark.django_db
def test_patient_search() -> None:
    o = OrganizationFactory.create(name="Test Organization")
    p = PatientFactory.create(first_name="John", last_name="Doe", organization=o)

    # don't match this one
    PatientFactory.create(
        first_name="Jane", last_name="Doe", organization=Organization.objects.create(name="Other Organization")
    )

    def search(query: str) -> list[Patient]:
        return list(Patient.objects.filter(organization=o).search(query))  # type: ignore[attr-defined]

    assert search("joh") == [p]
    assert search("john") == [p]
    assert search("doe") == [p]
    assert search("doe j") == [p]
    assert search("john d") == [p]
    assert search("john doe") == [p]
    assert search("  john  ") == [p]

    # don't match patients in another organization
    assert search("jane") == []
    assert search("jane doe") == []

    # punctuation shouldn't throw an error
    assert search("'steve") == []
    assert search("-steve") == []


def test_initials() -> None:
    p = Patient(first_name="John", last_name="Doe")
    assert p.initials() == "JD"

    p = Patient(first_name="Alice", last_name="Smith")
    assert p.initials() == "AS"

    p = Patient(first_name="Bob", last_name="")
    assert p.initials() == "B"

    p = Patient(first_name="", last_name="Brown")
    assert p.initials() == "B"

    p = Patient(first_name="", last_name="")
    assert p.initials() == ""


@pytest.mark.django_db
def test_patient_assign_user_owner_perms(user: User) -> None:
    patient = PatientFactory.create()

    assert user.has_perm("change_patient", patient) is False
    assert user.has_perm("delete_patient", patient) is False

    patient.assign_user_owner_perms(user)

    assert user.has_perm("change_patient", patient)
    assert user.has_perm("delete_patient", patient)
