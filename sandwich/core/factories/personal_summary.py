import factory
from factory.django import DjangoModelFactory

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models.personal_summary import PersonalSummary


class PersonalSummaryFactory(DjangoModelFactory[PersonalSummary]):
    class Meta:
        model = PersonalSummary

    patient = factory.SubFactory(PatientFactory)
    body = factory.Faker("text")
