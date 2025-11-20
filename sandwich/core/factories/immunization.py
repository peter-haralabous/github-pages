from datetime import timedelta

import factory
from django.utils import timezone
from factory.fuzzy import FuzzyDate

from sandwich.core.factories.health_record import HealthRecordFactory
from sandwich.core.models import Immunization


class ImmunizationFactory(HealthRecordFactory):
    class Meta:
        model = Immunization

    name = factory.Faker("immunization_name")
    date = FuzzyDate(start_date=timezone.now().date() - timedelta(weeks=10 * 52))
