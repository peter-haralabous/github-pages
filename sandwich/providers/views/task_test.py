from http import HTTPStatus

from django.test import Client
from django.urls import reverse
from guardian.shortcuts import remove_perm

from sandwich.core.factories.form import FormFactory
from sandwich.core.factories.form_submission import FormSubmissionFactory
from sandwich.core.factories.task import TaskFactory
from sandwich.core.models.form_submission import FormSubmissionStatus
from sandwich.core.models.organization import Organization
from sandwich.core.models.patient import Patient
from sandwich.core.models.role import RoleName
from sandwich.core.models.task import TaskStatus
from sandwich.users.models import User


def test_task_view(
    provider: User,
    organization: Organization,
    patient: Patient,
) -> None:
    client = Client()
    client.force_login(provider)
    task = TaskFactory.create(patient=patient)
    res = client.post(
        reverse(
            "providers:task", kwargs={"organization_id": organization.id, "patient_id": patient.id, "task_id": task.id}
        )
    )

    assert res.status_code == HTTPStatus.OK


def test_task_view_deny_access(
    provider: User,
    organization: Organization,
    patient: Patient,
) -> None:
    client = Client()
    client.force_login(provider)
    task = TaskFactory.create(patient=patient)
    # Gets the group of the provider (Staff) to remove the perm
    provider_group = organization.get_role(RoleName.STAFF).group
    remove_perm("view_task", provider_group, task)
    res = client.post(
        reverse(
            "providers:task", kwargs={"organization_id": organization.id, "patient_id": patient.id, "task_id": task.id}
        )
    )

    assert res.status_code == HTTPStatus.NOT_FOUND


def test_task_view_deny_access_no_org_acces(
    provider: User,
    organization: Organization,
    patient: Patient,
) -> None:
    client = Client()
    client.force_login(provider)
    task = TaskFactory.create(patient=patient)
    # Gets the group of the provider (Staff) to remove the perm
    provider_group = organization.get_role(RoleName.STAFF).group
    remove_perm("view_organization", provider_group, organization)
    res = client.post(
        reverse(
            "providers:task", kwargs={"organization_id": organization.id, "patient_id": patient.id, "task_id": task.id}
        )
    )

    assert res.status_code == HTTPStatus.NOT_FOUND


def test_task_view_deny_access_no_patient_access(
    provider: User,
    organization: Organization,
    patient: Patient,
) -> None:
    client = Client()
    client.force_login(provider)
    task = TaskFactory.create(patient=patient)
    # Gets the group of the provider (Staff) to remove the perm
    provider_group = organization.get_role(RoleName.STAFF).group
    remove_perm("view_patient", provider_group, patient)
    res = client.post(
        reverse(
            "providers:task", kwargs={"organization_id": organization.id, "patient_id": patient.id, "task_id": task.id}
        )
    )

    assert res.status_code == HTTPStatus.NOT_FOUND


def test_form_attached_to_task(patient: Patient, provider: User, organization: Organization) -> None:
    client = Client()
    client.force_login(provider)
    form = FormFactory.create(schema={"elements": [{"name": "test"}]})
    form_version = form.get_current_version()
    task = TaskFactory.create(patient=patient, form_version=form_version)
    url = reverse(
        "providers:task", kwargs={"patient_id": patient.id, "task_id": task.id, "organization_id": organization.id}
    )
    res = client.get(url)

    assert res.status_code == HTTPStatus.OK
    assert res.context["form_schema"] == {"elements": [{"name": "test"}]}


def test_form_submission_attached_to_form_task(patient: Patient, provider: User, organization: Organization) -> None:
    client = Client()
    client.force_login(provider)
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

    url = reverse(
        "providers:task", kwargs={"patient_id": patient.id, "task_id": task.id, "organization_id": organization.id}
    )
    res = client.get(url)

    assert res.status_code == HTTPStatus.OK
    assert "form_schema" in res.context
    assert res.context["read_only"] is True
    assert res.context["initial_data"] == submission.data


def test_complete_task_form_is_read_only(patient: Patient, provider: User, organization: Organization) -> None:
    client = Client()
    client.force_login(provider)
    task = TaskFactory.create(patient=patient, status=TaskStatus.COMPLETED)

    url = reverse(
        "providers:task", kwargs={"patient_id": patient.id, "task_id": task.id, "organization_id": organization.id}
    )
    res = client.get(url)

    assert res.status_code == HTTPStatus.OK
    assert res.context["read_only"] is True


def test_submit_and_save_draft_urls_exist(
    provider: User,
    organization: Organization,
    patient: Patient,
) -> None:
    client = Client()
    client.force_login(provider)
    task = TaskFactory.create(patient=patient, encounter__organization=organization)

    url = reverse(
        "providers:task", kwargs={"organization_id": organization.id, "patient_id": patient.id, "task_id": task.id}
    )

    res = client.get(url)

    submit_form_url = reverse("patients:patients-api:submit_form", kwargs={"task_id": str(task.id)})
    save_draft_url = reverse("patients:patients-api:save_draft_form", kwargs={"task_id": str(task.id)})

    assert submit_form_url in res.context["submit_url"]
    assert save_draft_url in res.context["save_draft_url"]
