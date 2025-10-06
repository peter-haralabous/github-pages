from http import HTTPStatus
from typing import TYPE_CHECKING
from typing import cast

from django.test import Client
from django.urls import reverse

from sandwich.core.factories import PatientFactory
from sandwich.users.models import User

if TYPE_CHECKING:
    from sandwich.core.models import Patient


def test_patient_http_get_urls_return_status_200(db, user) -> None:
    patient = cast("Patient", PatientFactory(user=user))
    client = Client()
    client.force_login(user)

    urls = [
        reverse("patients:patient_add"),
        reverse("patients:patient_details", kwargs={"patient_id": patient.pk}),
        reverse("patients:patient_edit", kwargs={"patient_id": patient.pk}),
    ]

    assert urls is not None, "No URLs to test"
    for url in urls:
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK, f"URL {url} returned {response.status_code}"


def test_patient_edit_post_updates_patient(db, user: User) -> None:
    patient = cast("Patient", PatientFactory(user=user, first_name="Old"))
    client = Client()
    client.force_login(user)
    url = reverse("patients:patient_edit", kwargs={"patient_id": patient.pk})
    data = {
        "first_name": "New",
        "last_name": patient.last_name,
        "email": patient.email,
        "phn": patient.phn,
        "date_of_birth": patient.date_of_birth,
    }
    response = client.post(url, data)
    assert response.status_code == HTTPStatus.FOUND
    patient.refresh_from_db()
    assert patient.first_name == "New"
