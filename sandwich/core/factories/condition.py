import factory

from sandwich.core.factories.health_record import HealthRecordFactory
from sandwich.core.models import Condition
from sandwich.core.models.condition import ConditionStatus


class ConditionFactory(HealthRecordFactory):
    class Meta:
        model = Condition

    name = factory.Faker("condition_name")
    status = ConditionStatus.ACTIVE
