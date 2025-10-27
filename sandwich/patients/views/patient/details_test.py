import pytest
from django.test import Client
from django.urls import reverse

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models import Fact
from sandwich.core.models.patient import Patient
from sandwich.users.models import User


@pytest.mark.django_db
def test_patient_details(user: User, patient: Patient) -> None:
    client = Client()
    client.force_login(user)
    res = client.get(
        reverse(
            "patients:patient_details",
            kwargs={
                "patient_id": patient.id,
            },
        )
    )

    assert res.status_code == 200


@pytest.mark.django_db
# NB: patient fixture required
def test_patient_details_deny_access(user: User, patient: Patient) -> None:
    other_patient = PatientFactory.create()
    client = Client()
    client.force_login(user)
    res = client.get(
        reverse(
            "patients:patient_details",
            kwargs={
                "patient_id": other_patient.id,
            },
        )
    )

    assert res.status_code == 404


def test_patient_details_kg(
    db, client: Client, user: User, patient: Patient, patient_knowledge_graph: list[Fact]
) -> None:
    client.force_login(user)
    url = reverse("patients:patient_details", kwargs={"patient_id": patient.pk})
    response = client.get(url)

    facts = response.context["facts"]

    category_length = {
        "allergies": 1,
        "conditions": 2,
        "documents_and_notes": 1,
        "family_history": 0,
        "hospital_visits": 0,
        "immunizations": 1,
        "injuries": 0,
        "lab_results": 0,
        "medications": 1,
        "practitioners": 0,
        "procedures": 1,
        "symptoms": 1,
    }
    all_categories = set(category_length.keys())
    assert set(facts.keys()) == all_categories, "Fact categories do not match expected categories."

    for category, length in category_length.items():
        assert len(facts[category]) == length, (
            f"Expected {length} facts in category '{category}', found {len(facts[category])}."
        )
