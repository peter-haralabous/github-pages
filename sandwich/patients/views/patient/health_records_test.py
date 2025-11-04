from django.test import Client
from django.urls import reverse

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models import Immunization
from sandwich.core.models import Patient
from sandwich.users.models import User


def test_add_and_remove_immunization(client: Client, user: User, patient: Patient):
    client.force_login(user)

    # get the "add" form
    response = client.get(
        reverse("patients:health_records_add", kwargs={"patient_id": patient.pk, "record_type": "immunization"})
    )
    assert response.status_code == 200

    # submit the "add" form
    response = client.post(
        reverse("patients:health_records_add", kwargs={"patient_id": patient.pk, "record_type": "immunization"}),
        data={
            "date": "2022-01-01",
            "name": "PCV13",
        },
    )
    assert response.status_code == 302  # redirects back to list view
    immunization = Immunization.objects.get(patient=patient)
    assert immunization.name == "PCV13"
    assert str(immunization.date) == "2022-01-01"

    # view the created record
    response = client.get(reverse("patients:immunization", kwargs={"immunization_id": immunization.pk}))
    assert response.status_code == 200

    # delete the created record
    response = client.delete(reverse("patients:immunization", kwargs={"immunization_id": immunization.pk}))
    assert response.status_code == 302  # redirects back to list view
    assert not Immunization.objects.filter(patient=patient).exists()


def test_immunization_not_accessible_to_other_patients(client: Client, user: User, patient: Patient):
    client.force_login(user)

    another_patient = PatientFactory.create()
    immunization = Immunization.objects.create(patient=another_patient, name="PCV13", date="2022-01-01")

    response = client.get(reverse("patients:immunization", kwargs={"immunization_id": immunization.pk}))
    assert response.status_code == 404
