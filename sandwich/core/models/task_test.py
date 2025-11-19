from unittest.mock import patch

import pytest
from django.db import models

from sandwich.core.factories.task import TaskFactory
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.form import Form
from sandwich.core.models.patient import Patient
from sandwich.core.models.task import Task
from sandwich.core.models.task import TaskStatus


def test_task_deletion_does_not_affect_form_version(db, encounter: Encounter) -> None:
    # create a form and form version
    form = Form.objects.create(name="Test Form", organization=encounter.organization)
    form_version = form.get_current_version()
    task = TaskFactory.create(form_version=form_version, encounter=encounter, patient=encounter.patient)
    assert task.form_version == form_version  # Task is linked to a specific form version
    task_id = task.id

    # when the task is deleted
    task.delete()

    # the form version should still exist
    form_version.refresh_from_db()
    assert form_version is not None
    with pytest.raises(Task.DoesNotExist):
        Task.objects.get(pk=task_id)  # but the task does not.


def test_referenced_form_version_is_protected_from_deletion(db, encounter: Encounter) -> None:
    form = Form.objects.create(name="Test Form", organization=encounter.organization)
    form_version = form.get_current_version()
    task = TaskFactory.create(form_version=form_version, encounter=encounter, patient=encounter.patient)
    assert task.form_version == form_version  # Task is linked to a specific form version

    # a referenced form version should not be deletable.
    with pytest.raises(models.deletion.ProtectedError):
        form_version.delete()

    # When the reference is removed...
    task.form_version = None
    task.save()

    # ...form version can be deleted.
    form_version.delete()

    assert form.events.count() == 0  # No versions exist anymore.


def test_task_creation_assigns_permissions(encounter: Encounter, patient: Patient) -> None:
    # You can find tests for assign_default_task_perms at
    # sandwich/core/service/task_service_test.py
    with patch("sandwich.core.service.task_service.assign_default_task_perms") as mock_permission_assignment:
        created = Task.objects.create(patient=patient, encounter=encounter, status=TaskStatus.READY)
        mock_permission_assignment.assert_called_once_with(created)
