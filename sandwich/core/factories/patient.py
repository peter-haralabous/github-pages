import factory
from factory.django import DjangoModelFactory

from sandwich.core.models import Patient


class PatientFactory(DjangoModelFactory[Patient]):
    class Meta:
        model = Patient

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    date_of_birth = factory.Faker("date_of_birth")
