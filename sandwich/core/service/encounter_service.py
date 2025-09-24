import logging

from django.utils import timezone

from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.patient import Patient
from sandwich.core.service.task_service import cancel_task

logger = logging.getLogger(__name__)


# NOTE-NG: It might feel like this belongs as a method on the Encounter model, but
# that doesn't scale well to actions that touch multiple objects (e.g. cancelling tasks)
# We don't want to have a dependency cycle between the Encounter and Task models.
def complete_encounter(encounter: Encounter) -> None:
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

    # Count active tasks before cancelling them
    active_tasks = encounter.task_set.filter(status__in=["REQUESTED", "IN_PROGRESS"])
    active_task_count = active_tasks.count()

    logger.debug(
        "Encounter completion details", extra={"encounter_id": encounter.id, "active_task_count": active_task_count}
    )

    encounter.status = EncounterStatus.COMPLETED
    encounter.ended_at = timezone.now()
    encounter.save()

    cancelled_task_count = 0
    for task in active_tasks:
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
