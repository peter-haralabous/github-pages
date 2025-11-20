import factory

from sandwich.core.models.health_record import HealthRecord


class HealthRecordFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HealthRecord
        abstract = True

    patient = factory.SubFactory("sandwich.core.factories.patient.PatientFactory")
    encounter = factory.SubFactory(
        "sandwich.core.factories.encounter.EncounterFactory", patient=factory.SelfAttribute("..patient")
    )
    unattested = True
