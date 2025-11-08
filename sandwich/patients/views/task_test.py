from http import HTTPStatus

from django.test import Client
from django.urls import reverse
from guardian.shortcuts import remove_perm

from sandwich.core.factories.form import FormFactory
from sandwich.core.factories.form_submission import FormSubmissionFactory
from sandwich.core.factories.task import TaskFactory
from sandwich.core.models.form_submission import FormSubmissionStatus
from sandwich.core.models.patient import Patient
from sandwich.core.models.task import TaskStatus
from sandwich.users.models import User


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

    assert res.status_code == HTTPStatus.OK


def test_form_attached_to_task(
    patient: Patient,
    user: User,
) -> None:
    client = Client()
    client.force_login(user)
    form = FormFactory.create(schema={"elements": [{"name": "test"}]})
    form_version = form.get_current_version()
    task = TaskFactory.create(patient=patient, form_version=form_version)
    url = reverse("patients:task", kwargs={"patient_id": patient.id, "task_id": task.id})
    res = client.get(url)

    assert res.status_code == HTTPStatus.OK
    assert res.context["form_schema"] == {"elements": [{"name": "test"}]}


def test_form_submission_attached_to_form_task(
    patient: Patient,
    user: User,
) -> None:
    client = Client()
    client.force_login(user)
    form = FormFactory.create()
    form_version = form.get_current_version()
    task = TaskFactory.create(patient=patient, form_version=form_version, status=TaskStatus.COMPLETED)
    submission = FormSubmissionFactory.create(
        form_version=form_version,
        task=task,
        patient=patient,
        data={"test": "data"},
        status=FormSubmissionStatus.COMPLETED,
    )

    url = reverse("patients:task", kwargs={"patient_id": patient.id, "task_id": task.id})
    res = client.get(url)

    assert res.status_code == HTTPStatus.OK
    assert "form_schema" in res.context
    assert res.context["read_only"] is True
    assert res.context["initial_data"] == submission.data


def test_complete_task_form_is_read_only(
    patient: Patient,
    user: User,
) -> None:
    client = Client()
    client.force_login(user)
    task = TaskFactory.create(patient=patient, status=TaskStatus.COMPLETED)

    url = reverse("patients:task", kwargs={"patient_id": patient.id, "task_id": task.id})
    res = client.get(url)

    assert res.status_code == HTTPStatus.OK
    assert res.context["read_only"] is True


def test_patient_denied_access_to_view_task_without_permission(
    patient: Patient,
    user: User,
) -> None:
    client = Client()
    client.force_login(user)
    task = TaskFactory.create(patient=patient)
    remove_perm("view_task", patient.user, task)
    url = reverse("patients:task", kwargs={"patient_id": patient.id, "task_id": task.id})
    res = client.get(url)

    assert res.status_code == HTTPStatus.NOT_FOUND


def test_task_view_includes_submit_url(client: Client, user: User, patient: Patient):
    """Request the patient task view and assert submit_url is provided."""

    task = TaskFactory.create(
        patient=patient,
        form_version=None,
    )

    client.force_login(user)

    url = reverse("patients:task", kwargs={"patient_id": patient.pk, "task_id": task.pk})
    response = client.get(url)

    # Ensure the view rendered and provided context
    assert response.status_code == HTTPStatus.OK
    assert "submit_url" in response.context

    submit_url = response.context["submit_url"]

    # We expect the URLs to end with the api paths for this task
    assert submit_url.endswith(f"/patients/api/form/{task.id}/submit")
