import pytest
from django.core.exceptions import PermissionDenied

from sandwich.core.factories.task import TaskFactory
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.organization import Organization
from sandwich.core.models.patient import Patient
from sandwich.core.models.task import TaskStatus
from sandwich.core.service.encounter_service import complete_encounter
from sandwich.users.models import User


def test_assign_default_encounter_perms(
    provider: User, user: User, organization: Organization, patient: Patient
) -> None:
    encounter = Encounter.objects.create(
        organization=organization, patient=patient, status=EncounterStatus.IN_PROGRESS
    )

    assert user.has_perm("view_encounter", encounter)

    assert provider.has_perm("view_encounter", encounter)
    assert provider.has_perm("change_encounter", encounter)


def test_complete_encounter(
    provider: User, encounter: Encounter, organization: Organization, patient: Patient
) -> None:
    task = TaskFactory.create(patient=patient, encounter=encounter)
    complete_encounter(encounter, provider)

    assert encounter.status == EncounterStatus.COMPLETED
    task.refresh_from_db()
    assert task.status == TaskStatus.CANCELLED


def test_complete_encounter_missing_task_perms(provider: User, encounter: Encounter, patient: Patient) -> None:
    task = TaskFactory.create(patient=patient, encounter=encounter)
    # This is admittedly a weird edge case to get into, but we should confirm
    # the user has permissions to cancel a task when completing an encounter.
    unpermissioned_task = TaskFactory.create(encounter=encounter)

    with pytest.raises(PermissionDenied):
        complete_encounter(encounter, provider)

    assert encounter.status == EncounterStatus.IN_PROGRESS

    task.refresh_from_db()
    assert task.status == TaskStatus.REQUESTED
    unpermissioned_task.refresh_from_db()
    assert unpermissioned_task.status == TaskStatus.REQUESTED
