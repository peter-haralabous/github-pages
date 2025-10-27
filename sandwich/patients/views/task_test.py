import pytest
from django.test import Client
from django.urls import reverse
from guardian.shortcuts import remove_perm

from sandwich.core.factories.task import TaskFactory
from sandwich.core.models.patient import Patient
from sandwich.users.models import User


@pytest.mark.django_db
def test_patient_can_view_assigned_task_with_permission(
    patient: Patient,
    user: User,
) -> None:
    client = Client()
    # Ensure the patient's user is the one logging in
    client.force_login(user)
    task = TaskFactory.create(patient=patient)
    url = reverse("patients:task", kwargs={"patient_id": patient.id, "task_id": task.id})
    res = client.get(url)

    assert res.status_code == 200


@pytest.mark.django_db
def test_patient_denied_access_to_view_task_without_permission(
    patient: Patient,
    user: User,
) -> None:
    client = Client()
    # Ensure the patient's user is the one logging in
    client.force_login(user)
    task = TaskFactory.create(patient=patient)
    remove_perm("view_task", patient.user, task)
    url = reverse("patients:task", kwargs={"patient_id": patient.id, "task_id": task.id})
    res = client.get(url)

    assert res.status_code == 404
