from django.test import Client
from django.urls import reverse

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models import Encounter
from sandwich.core.models import Organization
from sandwich.core.models.encounter import EncounterStatus
from sandwich.providers.views.search import _patient_search_results
from sandwich.users.models import User


def add_patients_and_encounters(organization: Organization) -> None:
    # the first patient has an active encounter
    patient1 = PatientFactory.create(
        organization=organization,
        first_name="John",
        last_name="Doe",
        date_of_birth="1990-01-01",
    )
    Encounter.objects.create(
        organization=organization,
        patient=patient1,
        status=EncounterStatus.IN_PROGRESS,
    )

    # the second patient has no encounters
    PatientFactory.create(
        organization=organization,
        first_name="Jane",
        last_name="Smith",
        date_of_birth="1985-05-15",
    )

    # the third patient has two encounters
    patient3 = PatientFactory.create(
        organization=organization,
        first_name="Kevin",
        last_name="Smith",
    )
    Encounter.objects.create(
        organization=organization,
        patient=patient3,
        status=EncounterStatus.IN_PROGRESS,
    )
    Encounter.objects.create(
        organization=organization,
        patient=patient3,
        status=EncounterStatus.COMPLETED,
    )


def test_patient_search_results(organization: Organization) -> None:
    add_patients_and_encounters(organization)

    assert len(_patient_search_results(organization, "John")) == 1
    assert len(_patient_search_results(organization, "Jane")) == 1
    assert len(_patient_search_results(organization, "Kevin")) == 1

    results = _patient_search_results(organization, "Smith")
    assert len(results) == 2
    # order matters: active encounter first, then completed encounter, then no encounters
    assert results[0].title == "Kevin Smith"
    assert results[0].encounter.active is True  # type: ignore[union-attr]
    assert results[1].title == "Jane Smith"
    assert results[1].encounter is None


def test_search(client: Client, organization: Organization, provider: User) -> None:
    client.force_login(provider)
    add_patients_and_encounters(organization)

    url = reverse("providers:search", kwargs={"organization_id": organization.id})

    # Test searching with no query
    response = client.get(url)
    assert response.status_code == 200
    assert "Create a new patient" in response.content.decode()

    # Test searching for an existing patient by name
    response = client.get(url, {"q": "John"})
    assert response.status_code == 200
    content = response.content.decode()
    assert "John Doe" in content
    assert "Jane Smith" not in content
    assert "Kevin Smith" not in content
    assert "Create patient" in content

    # Test searching for an existing patient by last name
    response = client.get(url, {"q": "Smith"})
    assert response.status_code == 200
    content = response.content.decode()
    assert "Jane Smith" in content
    assert "Kevin Smith" in content
    assert "John Doe" not in content
    assert "Create patient" in content

    # Test searching for a non-existing patient
    response = client.get(url, {"q": "Nonexistent"})
    assert response.status_code == 200
    content = response.content.decode()
    assert "Create patient" in content
    assert "John Doe" not in content
    assert "Jane Smith" not in content
    assert "Kevin Smith" not in content
