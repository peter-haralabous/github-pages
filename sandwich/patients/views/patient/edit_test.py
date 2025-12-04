from http import HTTPStatus
from typing import Any

import pytest
from django.test import Client
from django.urls import reverse

from sandwich.core.models import Patient
from sandwich.patients.views.patient.edit import PatientEdit
from sandwich.users.models import User


@pytest.mark.django_db
def test_patient_edit_post_updates_patient(db, patient: Patient, user: User) -> None:
    client = Client()
    client.force_login(user)
    url = reverse("patients:patient_edit", kwargs={"patient_id": patient.pk})
    data = {
        "first_name": "New",
        "last_name": patient.last_name,
        "date_of_birth": patient.date_of_birth,
        "province": "BC",
        "phn": "9111111117",  # BC requires more specific PHN
    }
    response = client.post(url, data)
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers.get("Location") == reverse("patients:patient_edit", kwargs={"patient_id": patient.id})
    patient.refresh_from_db()
    assert patient.first_name == "New"


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
def test_patient_edit_form(data: dict[str, Any], *, is_valid: bool) -> None:
    patient_form = PatientEdit(data)
    assert patient_form.is_valid() == is_valid
