import pytest
from django.test import Client
from django.urls import reverse
from guardian.shortcuts import remove_perm

from sandwich.core.factories.task import TaskFactory
from sandwich.core.models.organization import Organization
from sandwich.core.models.patient import Patient
from sandwich.core.models.role import RoleName
from sandwich.users.models import User


@pytest.mark.django_db
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

    assert res.status_code == 200


@pytest.mark.django_db
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

    assert res.status_code == 403
