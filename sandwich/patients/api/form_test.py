import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time
from guardian.shortcuts import remove_perm

from sandwich.core.factories.form import FormFactory

# Import your models, factories, and services
from sandwich.core.factories.task import TaskFactory
from sandwich.core.models import Form
from sandwich.core.models import Organization
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

    payload = {"q1": "Final Answer"}
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
    assert submission.submitted_by == user


@pytest.mark.django_db
def test_submit_form_no_permission(user: User, encounter: Encounter, patient: Patient):
    """
    Tests that a user without permission gets an error
    """
    client = Client()
    client.force_login(user)
    task = TaskFactory.create(encounter=encounter, patient=patient)

    payload = {"q1": "Final Answer"}
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

    payload = {"q1": "Trying to submit"}
    url = reverse("patients:api-1.0.0:submit_form", kwargs={"task_id": task.id})

    response = client.post(url, data=payload, content_type="application/json")

    assert response.status_code == 400
    assert response.json()["detail"] == "This form has already been submitted"


@pytest.mark.django_db
def test_save_draft_form_creates_new_draft(user: User, encounter: Encounter, patient: Patient):
    """
    Tests that the save_draft endpoint creates a new draft submission
    if one doesn't exist.
    """
    client = Client()
    client.force_login(user)
    task = TaskFactory.create(encounter=encounter, patient=patient)

    payload = {"q1": "Draft Answer"}
    url = reverse("patients:api-1.0.0:save_draft_form", kwargs={"task_id": task.id})

    response = client.post(url, data=payload, content_type="application/json")

    assert response.status_code == 200
    assert (submission := FormSubmission.objects.get(task=task, patient=task.patient))
    assert submission.data == {"q1": "Draft Answer"}
    assert submission.status == FormSubmissionStatus.DRAFT
    assert submission.submitted_at is None
    assert submission.form_version == task.form_version


@pytest.mark.django_db
def test_save_draft_form_success_updates_existing_draft(user: User, encounter: Encounter, patient: Patient):
    """
    Tests that the save_draft endpoint updates an existing draft submission.
    """
    client = Client()
    client.force_login(user)
    task = TaskFactory.create(encounter=encounter, patient=patient)

    # Create an initial draft submission
    submission = FormSubmission.objects.create(
        task=task,
        patient=task.patient,
        form_version=task.form_version,
        status=FormSubmissionStatus.DRAFT,
        data={"q1": "Old Answer"},
    )

    payload = {"q1": "New Draft Answer", "q2": "Added Q2"}
    url = reverse("patients:api-1.0.0:save_draft_form", kwargs={"task_id": task.id})

    response = client.post(url, data=payload, content_type="application/json")

    assert response.status_code == 200

    submission.refresh_from_db()
    assert submission.data == {"q1": "New Draft Answer", "q2": "Added Q2"}
    assert submission.status == FormSubmissionStatus.DRAFT
    assert submission.submitted_at is None


@pytest.mark.django_db
def test_save_draft_form_no_permission(user: User, encounter: Encounter, patient: Patient):
    """
    Tests that a user without 'complete_task' permission gets an error
    when trying to save a draft.
    """
    client = Client()
    client.force_login(user)
    task = TaskFactory.create(encounter=encounter, patient=patient)

    remove_perm("complete_task", patient.user, task)

    payload = {"q1": "Draft Answer"}
    url = reverse("patients:api-1.0.0:save_draft_form", kwargs={"task_id": task.id})

    response = client.post(url, data=payload, content_type="application/json")

    assert response.status_code == 404


@pytest.mark.django_db
def test_save_draft_form_on_completed_submission(user: User, encounter: Encounter, patient: Patient):
    """
    Tests that saving a draft to an already completed form returns a 400 error.
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
        data={"q1": "Final Answer"},
    )

    payload = {"q1": "Trying to overwrite completed draft"}
    url = reverse("patients:api-1.0.0:save_draft_form", kwargs={"task_id": task.id})

    response = client.post(url, data=payload, content_type="application/json")

    assert response.status_code == 400
    assert response.json()["detail"] == "This form has already been submitted"


def test_provider_form_create(client: Client, owner: User, organization: Organization):
    orgs_forms = Form.objects.filter(organization=organization)
    assert orgs_forms.exists() is False

    client.force_login(owner)
    payload = {"title": "Intake Form"}
    url = reverse("patients:api-1.0.0:provider_form_create", kwargs={"organization_id": organization.id})
    response = client.post(url, data=payload, content_type="application/json")

    created_form = orgs_forms.first()
    assert created_form is not None
    assert response.status_code == 200
    assert response.json()["form_id"] == str(created_form.id)
    assert response.json()["message"] == "Form created successfully"


def test_provider_form_create_validation(client: Client, owner: User, organization: Organization):
    """If the user does not provide a form title, endpoint returns 400 error."""
    client.force_login(owner)
    payload = {"width": "1000px"}
    url = reverse("patients:api-1.0.0:provider_form_create", kwargs={"organization_id": organization.id})
    response = client.post(url, data=payload, content_type="application/json")

    assert response.status_code == 400
    assert response.json()["detail"] == "Form must include a title: 'General' section missing 'Survey title'"


def test_provider_form_create_duplicate_form_name(client: Client, owner: User, organization: Organization):
    """Creating a form with the same as an existing one in the organization returns 400 error."""
    existing_form = FormFactory.create(organization=organization, name="Intake Form")

    client.force_login(owner)
    payload = {"title": existing_form.name}
    url = reverse("patients:api-1.0.0:provider_form_create", kwargs={"organization_id": organization.id})
    response = client.post(url, data=payload, content_type="application/json")

    assert response.status_code == 400
    assert response.json()["detail"] == "Form with same title already exists. Please choose a different title."
