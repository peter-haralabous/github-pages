import logging

from django.core.exceptions import PermissionDenied
from django.utils import timezone
from guardian.shortcuts import assign_perm
from guardian.shortcuts import get_objects_for_user

from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.patient import Patient
from sandwich.core.models.role import RoleName
from sandwich.core.service.task_service import cancel_task
from sandwich.users.models import User

logger = logging.getLogger(__name__)


# NOTE-NG: It might feel like this belongs as a method on the Encounter model, but
# that doesn't scale well to actions that touch multiple objects (e.g. cancelling tasks)
# We don't want to have a dependency cycle between the Encounter and Task models.
def complete_encounter(encounter: Encounter, user: User) -> None:
    """Mark an encounter as completed; cancel any outstanding tasks associated with it."""
    logger.info(
        "Completing encounter",
        extra={
            "encounter_id": encounter.id,
            "patient_id": encounter.patient.id,
            "organization_id": encounter.organization.id,
        },
    )

    assert encounter.active, "Cannot complete an inactive encounter."

    active_tasks = encounter.task_set.filter(status__in=["REQUESTED", "IN_PROGRESS"])

    # Ensure user has perms to change these tasks
    authorized_active_tasks = get_objects_for_user(user, ["view_task", "change_task"], active_tasks)
    for task in active_tasks:
        if task not in authorized_active_tasks:
            raise PermissionDenied(f"You do not have permissions to cancel task {task.id} in this encounter.")

    # Count active tasks before cancelling them
    active_task_count = authorized_active_tasks.count()

    logger.debug(
        "Encounter completion details", extra={"encounter_id": encounter.id, "active_task_count": active_task_count}
    )

    encounter.status = EncounterStatus.COMPLETED
    encounter.ended_at = timezone.now()
    encounter.save()

    cancelled_task_count = 0
    for task in authorized_active_tasks:
        if task.active:
            cancel_task(task)
            cancelled_task_count += 1

    logger.info(
        "Encounter completed successfully",
        extra={
            "encounter_id": encounter.id,
            "patient_id": encounter.patient.id,
            "cancelled_task_count": cancelled_task_count,
        },
    )


def get_current_encounter(patient: Patient) -> Encounter | None:
    """Get the current active encounter for a patient."""
    logger.debug(
        "Retrieving current encounter for patient",
        extra={"patient_id": patient.id, "organization_id": getattr(patient.organization, "id", "unknown")},
    )

    # TODO-NG: enforce that there is only one active encounter per patient?
    # TODO-NG: does this belong on the patient model?
    encounter = patient.encounter_set.filter(status=EncounterStatus.IN_PROGRESS).first()

    logger.debug(
        "Current encounter query result",
        extra={
            "patient_id": patient.id,
            "has_current_encounter": bool(encounter),
            "encounter_id": encounter.id if encounter else None,
        },
    )

    return encounter


DEFAULT_ORGANIZATION_ROLE_PERMS = {
    RoleName.OWNER: ["change_encounter", "view_encounter"],
    RoleName.ADMIN: ["change_encounter", "view_encounter"],
    RoleName.STAFF: ["change_encounter", "view_encounter"],
}


def assign_default_encounter_perms(encounter: Encounter) -> None:
    # Apply org-wide role perms
    for role_name, perms in DEFAULT_ORGANIZATION_ROLE_PERMS.items():
        role = encounter.organization.get_role(role_name)
        for perm in perms:
            assign_perm(perm, role.group, encounter)

    # Apply encounter-user perms
    if encounter.patient.user:
        assign_perm("view_encounter", encounter.patient.user, encounter)
