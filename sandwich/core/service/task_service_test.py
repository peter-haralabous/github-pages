import pytest

from sandwich.core.factories.task import TaskFactory
from sandwich.core.models import Task
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.patient import Patient
from sandwich.core.service.invitation_service_test import mask_uuids
from sandwich.core.service.task_service import assign_default_task_perms
from sandwich.core.service.task_service import send_task_added_email
from sandwich.users.models import User


@pytest.mark.django_db
def test_send_task_added_email(template_fixture: None, task: Task, mailoutbox, snapshot):
    send_task_added_email(task)
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [task.patient.email]

    # if the template changes, the snapshot will need to be updated
    assert mask_uuids(mailoutbox[0].body) == snapshot


@pytest.mark.django_db
def test_assign_default_provider_task_perms(
    encounter: Encounter,
    patient: Patient,
    provider: User,
) -> None:
    task = TaskFactory.create(patient=patient, encounter=encounter)
    assign_default_task_perms(task)

    assert provider.has_perm("view_task", task)

    assert provider.has_perm("complete_task", task)
    assert provider.has_perm("change_task", task)
