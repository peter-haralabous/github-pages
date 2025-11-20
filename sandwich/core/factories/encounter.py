import factory

from sandwich.core.models import Encounter
from sandwich.core.models.encounter import EncounterStatus


class EncounterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Encounter

    organization = factory.SubFactory("sandwich.core.factories.organization.OrganizationFactory")
    patient = factory.SubFactory("sandwich.core.factories.patient.PatientFactory")
    status = EncounterStatus.IN_PROGRESS
