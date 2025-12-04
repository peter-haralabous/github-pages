from typing import cast

from django.test import Client
from django.urls import reverse

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models import Condition
from sandwich.core.models import Immunization
from sandwich.core.models import Patient
from sandwich.core.models import Practitioner
from sandwich.core.models.condition import ConditionStatus
from sandwich.core.models.health_record import HealthRecordType
from sandwich.patients.views.patient.health_records import HistoryEvent
from sandwich.patients.views.patient.health_records import _history_events
from sandwich.users.models import User


def test_add_and_remove_immunization(client: Client, user: User, patient: Patient):
    client.force_login(user)

    # get the "add" form
    response = client.get(
        reverse(
            "patients:health_records_add",
            kwargs={"patient_id": patient.pk, "record_type": HealthRecordType.IMMUNIZATION},
        )
    )
    assert response.status_code == 200

    # submit the "add" form
    response = client.post(
        reverse(
            "patients:health_records_add",
            kwargs={"patient_id": patient.pk, "record_type": HealthRecordType.IMMUNIZATION},
        ),
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


def test_add_update_and_remove_practitioner(client: Client, user: User, patient: Patient):
    client.force_login(user)

    # get the "add" form
    response = client.get(
        reverse(
            "patients:health_records_add",
            kwargs={"patient_id": patient.pk, "record_type": HealthRecordType.PRACTITIONER},
        )
    )
    assert response.status_code == 200

    # submit the "add" form
    response = client.post(
        reverse(
            "patients:health_records_add",
            kwargs={"patient_id": patient.pk, "record_type": HealthRecordType.PRACTITIONER},
        ),
        data={
            "name": "Dr. Jekyll",
        },
    )
    assert response.status_code == 302  # redirects back to list view
    practitioner = Practitioner.objects.get(patient=patient)
    assert practitioner.name == "Dr. Jekyll"

    # view the created record
    response = client.get(reverse("patients:practitioner", kwargs={"practitioner_id": practitioner.pk}))
    assert response.status_code == 200

    # update the created record
    response = client.post(
        reverse("patients:practitioner", kwargs={"practitioner_id": practitioner.pk}), data={"name": "Mr. Hyde"}
    )
    assert response.status_code == 302  # redirects back to list view
    practitioner.refresh_from_db()
    assert practitioner.name == "Mr. Hyde"

    # delete the created record
    response = client.delete(reverse("patients:practitioner", kwargs={"practitioner_id": practitioner.pk}))
    assert response.status_code == 302  # redirects back to list view
    assert not Practitioner.objects.filter(patient=patient).exists()


def test_add_condition(client: Client, user: User, patient: Patient):
    client.force_login(user)

    # get the "add" form
    response = client.get(
        reverse(
            "patients:health_records_add", kwargs={"patient_id": patient.pk, "record_type": HealthRecordType.CONDITION}
        )
    )
    assert response.status_code == 200

    # submit the "add" form
    response = client.post(
        reverse(
            "patients:health_records_add", kwargs={"patient_id": patient.pk, "record_type": HealthRecordType.CONDITION}
        ),
        data={
            "name": "Cancer",
            "status": "remission",
        },
    )
    assert response.status_code == 302  # redirects back to list view
    condition = Condition.objects.get(patient=patient)
    assert condition.name == "Cancer"
    assert condition.status == ConditionStatus.REMISSION


def test_one_history_entry(user: User, patient: Patient):
    practitioner = Practitioner.objects.create(patient=patient, name="Doctor")

    assert practitioner.get_total_versions() == 1
    history = _history_events(practitioner, user, limit=1)
    assert len(history) == 1
    assert cast("HistoryEvent", history[0]).label == "insert"


def test_many_history_entries(user: User, patient: Patient):
    practitioner = Practitioner.objects.create(patient=patient, name="Doctor")

    for i in range(1, 100):
        practitioner.name = f"Doctor {i}"
        practitioner.save()

    assert practitioner.get_total_versions() == 100
    history = _history_events(practitioner, user, limit=3)
    assert len(history) == 4
    assert cast("HistoryEvent", history[0]).label == "update"
    assert cast("HistoryEvent", history[1]).label == "update"
    assert str(history[2]) == "97 more..."
    assert cast("HistoryEvent", history[3]).label == "insert"
