from datetime import timedelta

import pytest
from django.utils import timezone

from sandwich.core.factories.task import TaskFactory
from sandwich.core.models import Task
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.patient import Patient
from sandwich.core.models.task import TaskStatus
from sandwich.core.service.invitation_service_test import mask_uuids
from sandwich.core.service.task_service import ordered_tasks_for_encounter
from sandwich.core.service.task_service import send_task_added_email
from sandwich.users.models import User


@pytest.mark.django_db
def test_send_task_added_email(template_fixture: None, task: Task, mailoutbox, snapshot_html):
    send_task_added_email(task)
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [task.patient.email]

    # if the template changes, the snapshot will need to be updated
    assert mask_uuids(mailoutbox[0].body) == snapshot_html


@pytest.mark.django_db
def test_assign_default_provider_task_perms(
    encounter: Encounter,
    patient: Patient,
    provider: User,
) -> None:
    task = TaskFactory.create(patient=patient, encounter=encounter)

    assert provider.has_perm("view_task", task)

    assert provider.has_perm("complete_task", task)
    assert provider.has_perm("change_task", task)


@pytest.mark.django_db
def test_ordered_tasks_for_encounter(encounter: Encounter, patient: Patient) -> None:
    active_task_1 = TaskFactory.create(patient=patient, encounter=encounter, status=TaskStatus.IN_PROGRESS)
    active_task_2 = TaskFactory.create(patient=patient, encounter=encounter, status=TaskStatus.READY)
    archived_task_1 = TaskFactory.create(patient=patient, encounter=encounter, status=TaskStatus.COMPLETED)
    archived_task_2 = TaskFactory.create(patient=patient, encounter=encounter, status=TaskStatus.CANCELLED)

    base = timezone.now()
    Task.objects.filter(id=active_task_1.id).update(updated_at=base)
    Task.objects.filter(id=active_task_2.id).update(updated_at=base - timedelta(minutes=5))
    Task.objects.filter(id=archived_task_1.id).update(updated_at=base - timedelta(minutes=10))
    Task.objects.filter(id=archived_task_2.id).update(updated_at=base - timedelta(minutes=15))

    # Refresh instances to pick up updated_at changes
    for t in (active_task_1, active_task_2, archived_task_1, archived_task_2):
        t.refresh_from_db()

    ordered_tasks = ordered_tasks_for_encounter(encounter)
    assert ordered_tasks == [active_task_1, active_task_2, archived_task_1, archived_task_2]
