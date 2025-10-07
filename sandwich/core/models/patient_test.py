import pytest

from sandwich.core.factories import OrganizationFactory
from sandwich.core.factories import PatientFactory
from sandwich.core.models import Organization
from sandwich.core.models import Patient


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
