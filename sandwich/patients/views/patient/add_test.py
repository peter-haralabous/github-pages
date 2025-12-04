from datetime import date
from http import HTTPStatus
from typing import Any

import pytest
from django.test import Client
from django.urls import reverse

from sandwich.core.models import Patient
from sandwich.patients.views.patient.add import PatientAdd
from sandwich.users.models import User


@pytest.mark.django_db
# NB: patient fixture required, user needs a patient to bypass profile creation
def test_patient_add(db, user: User, patient: Patient) -> None:
    client = Client()
    client.force_login(user)
    url = reverse("patients:patient_add")
    data = {
        "first_name": "Jacob",
        "last_name": "Newpatient",
        "date_of_birth": date(1961, 6, 6),
        "province": "BC",
        "phn": "9111111117",  # BC requires more specific PHN
    }
    response = client.post(url, data)
    created_patient = Patient.objects.get(last_name="Newpatient")
    assert created_patient
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers.get("Location") == reverse(
        "patients:patient_details", kwargs={"patient_id": created_patient.id}
    )
    assert user.has_perm("change_patient", created_patient)


@pytest.mark.django_db
def test_patient_onboarding_add(db, user: User) -> None:
    client = Client()
    client.force_login(user)
    url = reverse("patients:patient_onboarding_add")
    data = {
        "first_name": "Jacob",
        "last_name": "Newpatient",
        "date_of_birth": date(1961, 6, 6),
        "province": "BC",
        "phn": "9111111117",  # BC requires more specific PHN
    }
    response = client.post(url, data)
    created_patient = Patient.objects.get(last_name="Newpatient")
    assert created_patient
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers.get("Location") == reverse("patients:home")
    assert user.has_perm("change_patient", created_patient)


@pytest.mark.django_db
def test_patient_onboarding_add_not_accessible(db, user: User, patient: Patient) -> None:
    client = Client()
    client.force_login(user)
    url = reverse("patients:patient_onboarding_add")
    response = client.get(url)
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
        pytest.param(
            {
                "first_name": "Tad",
                "last_name": "Cooper",
                "date_of_birth": "1961-11-11",
                "province": "BC",
                "phn": "9111111117",
            },
            True,
            id="Pass: BC phn is valid",
        ),
        pytest.param(
            {
                "first_name": "Tad",
                "last_name": "Cooper",
                "date_of_birth": "1961-11-11",
                "province": "BC",
                "phn": "9111111119",
            },
            False,
            id="Fail: BC phn is not valid",
        ),
    ],
)
def test_patient_create_form(data: dict[str, Any], *, is_valid: bool) -> None:
    patient_form = PatientAdd(data)
    assert patient_form.is_valid() == is_valid
