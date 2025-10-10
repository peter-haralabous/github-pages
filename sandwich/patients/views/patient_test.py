from http import HTTPStatus
from typing import Any

import pytest
from django.test import Client
from django.urls import reverse

from sandwich.core.factories import PatientFactory
from sandwich.core.models.patient import Patient
from sandwich.patients.views.patient import PatientAdd
from sandwich.patients.views.patient import PatientEdit
from sandwich.users.models import User


@pytest.mark.django_db
def test_patient_edit_post_updates_patient(db, user: User) -> None:
    patient = PatientFactory.create(user=user, first_name="Old")
    client = Client()
    client.force_login(user)
    url = reverse("patients:patient_edit", kwargs={"patient_id": patient.pk})
    data = {
        "first_name": "New",
        "last_name": patient.last_name,
        "date_of_birth": patient.date_of_birth,
        "province": "BC",
        "phn": patient.phn,
    }
    response = client.post(url, data)
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers.get("Location") == reverse("patients:patient_details", kwargs={"patient_id": patient.id})
    patient.refresh_from_db()
    assert patient.first_name == "New"


@pytest.mark.django_db
def test_patient_add(db, user: User) -> None:
    # Needs an existing patient so we don't get redirected to onboarding_add
    existing_patient = PatientFactory.create(user=user)
    existing_patient.save()

    patient = PatientFactory.create()
    client = Client()
    client.force_login(user)
    url = reverse("patients:patient_add")
    data = {
        "first_name": patient.first_name,
        "last_name": "Newpatient",
        "date_of_birth": patient.date_of_birth,
        "province": "BC",
        "phn": patient.phn,
    }
    response = client.post(url, data)
    created_patient = Patient.objects.get(last_name="Newpatient", date_of_birth=patient.date_of_birth)
    assert created_patient
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers.get("Location") == reverse(
        "patients:patient_details", kwargs={"patient_id": created_patient.id}
    )


@pytest.mark.django_db
def test_patient_onboarding_add(db, user: User) -> None:
    patient = PatientFactory.create()
    client = Client()
    client.force_login(user)
    url = reverse("patients:patient_onboarding_add")
    data = {
        "first_name": patient.first_name,
        "last_name": "Newpatient",
        "date_of_birth": patient.date_of_birth,
        "province": "BC",
        "phn": patient.phn,
    }
    response = client.post(url, data)
    created_patient = Patient.objects.get(last_name="Newpatient", date_of_birth=patient.date_of_birth)
    assert created_patient
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers.get("Location") == reverse("patients:home")


@pytest.mark.parametrize(
    ("data", "is_valid"),
    [
        pytest.param(
            {
                "first_name": "Tad",
                "last_name": "Cooper",
                "date_of_birth": "1961-11-11",
            },
            True,
            id="Pass: All required fields present, date in past.",
        ),
        pytest.param(
            {
                "first_name": "Tad",
                "last_name": "Cooper",
                "date_of_birth": "2500-11-11",
            },
            False,
            id="Fail: date of birth in future",
        ),
        pytest.param(
            {
                "last_name": "Cooper",
                "date_of_birth": "1961-11-11",
            },
            False,
            id="Fail: missing required field",
        ),
    ],
)
def test_patient_edit_form(data: dict[str, Any], *, is_valid: bool) -> None:
    patient_form = PatientEdit(data)
    assert patient_form.is_valid() == is_valid


@pytest.mark.parametrize(
    ("data", "is_valid"),
    [
        pytest.param(
            {
                "first_name": "Tad",
                "last_name": "Cooper",
                "date_of_birth": "1961-11-11",
            },
            True,
            id="Pass: All required fields present, date in past.",
        ),
        pytest.param(
            {
                "first_name": "Tad",
                "last_name": "Cooper",
                "date_of_birth": "2500-11-11",
            },
            False,
            id="Fail: date of birth in future",
        ),
        pytest.param(
            {
                "last_name": "Cooper",
                "date_of_birth": "1961-11-11",
            },
            False,
            id="Fail: missing required field",
        ),
    ],
)
def test_patient_create_form(data: dict[str, Any], *, is_valid: bool) -> None:
    patient_form = PatientAdd(data)
    assert patient_form.is_valid() == is_valid
