import factory
from factory.django import DjangoModelFactory

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models import Task
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.task import TaskStatus


class TaskFactory(DjangoModelFactory[Task]):
    class Meta:
        model = Task

    patient = factory.SubFactory(PatientFactory)
    encounter = factory.LazyAttribute(
        lambda o: Encounter.objects.create(
            patient=o.patient, organization=o.patient.organization, status=EncounterStatus.UNKNOWN
        )
    )

    status = TaskStatus.REQUESTED
