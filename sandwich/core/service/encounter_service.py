from django.utils import timezone

from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.patient import Patient
from sandwich.core.service.task_service import cancel_task


# NOTE-NG: It might feel like this belongs as a method on the Encounter model, but
# that doesn't scale well to actions that touch multiple objects (e.g. cancelling tasks)
# We don't want to have a dependency cycle between the Encounter and Task models.
def complete_encounter(encounter: Encounter) -> None:
    """Mark an encounter as completed; cancel any outstanding tasks associated with it."""
    assert encounter.active, "Cannot complete an inactive encounter."

    encounter.status = EncounterStatus.COMPLETED
    encounter.ended_at = timezone.now()
    encounter.save()

    for task in encounter.task_set.all():
        if task.active:
            cancel_task(task)


def get_current_encounter(patient: Patient) -> Encounter | None:
    """Get the current active encounter for a patient."""
    # TODO-NG: enforce that there is only one active encounter per patient?
    # TODO-NG: does this belong on the patient model?
    return patient.encounter_set.filter(status=EncounterStatus.IN_PROGRESS).first()
