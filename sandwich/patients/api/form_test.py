import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time
from guardian.shortcuts import remove_perm

# Import your models, factories, and services
from sandwich.core.factories.task import TaskFactory
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.form_submission import FormSubmission
from sandwich.core.models.form_submission import FormSubmissionStatus
from sandwich.core.models.patient import Patient
from sandwich.users.models import User


@pytest.mark.django_db
def test_submit_form_success(user: User, encounter: Encounter, patient: Patient):
    """
    Tests a user with correct permissions submits a completed form
    """

    client = Client()
    client.force_login(user)
    task = TaskFactory.create(encounter=encounter, patient=patient)

    payload = {"data": {"q1": "Final Answer"}}
    url = reverse("patients:api-1.0.0:submit_form", kwargs={"task_id": task.id})

    frozen_time = timezone.now()
    with freeze_time(frozen_time):
        response = client.post(url, data=payload, content_type="application/json")

    assert response.status_code == 200
    assert (submission := FormSubmission.objects.get(task=task, patient=task.patient))
    assert submission.data == {"q1": "Final Answer"}
    assert submission.status == FormSubmissionStatus.COMPLETED
    assert submission.form_version == task.form_version
    assert submission.submitted_at == frozen_time


@pytest.mark.django_db
def test_submit_form_no_permission(user: User, encounter: Encounter, patient: Patient):
    """
    Tests that a user without permission gets an error
    """
    client = Client()
    client.force_login(user)
    task = TaskFactory.create(encounter=encounter, patient=patient)

    payload = {"data": {"q1": "Final Answer"}}
    remove_perm("complete_task", patient.user, task)
    url = reverse("patients:api-1.0.0:submit_form", kwargs={"task_id": task.id})

    response = client.post(url, data=payload, content_type="application/json")

    assert response.status_code == 404


@pytest.mark.django_db
def test_submit_form_already_completed(user: User, encounter: Encounter, patient: Patient):
    """
    Tests that submitting an already completed form returns a 400 error.
    """
    client = Client()
    client.force_login(user)
    task = TaskFactory.create(encounter=encounter, patient=patient)

    # Create a submission that is already COMPLETED
    FormSubmission.objects.create(
        task=task,
        patient=task.patient,
        form_version=task.form_version,
        status=FormSubmissionStatus.COMPLETED,
    )

    payload = {"data": {"q1": "Trying to submit"}}
    url = reverse("patients:api-1.0.0:submit_form", kwargs={"task_id": task.id})

    response = client.post(url, data=payload, content_type="application/json")

    assert response.status_code == 400
    assert response.json()["detail"] == "This form has already been submitted"
