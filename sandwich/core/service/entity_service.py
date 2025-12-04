import typing

from sandwich.core.models import Entity
from sandwich.core.models.entity import EntityType

if typing.TYPE_CHECKING:
    from sandwich.core.models import Patient


def entity_for_patient(patient: "Patient") -> Entity:
    return Entity.objects.get_or_create(
        type=EntityType.PATIENT,
        patient=patient,
        defaults={
            "type": EntityType.PATIENT,
            "patient": patient,
            "metadata": {"label": patient.full_name},
        },
    )[0]
