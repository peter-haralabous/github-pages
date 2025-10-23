import factory

from sandwich.core.factories.errors import FactoryError
from sandwich.core.models import Entity
from sandwich.core.models import Fact
from sandwich.core.models import Patient
from sandwich.core.models import Predicate
from sandwich.core.models.entity import EntityType
from sandwich.core.models.predicate import PredicateName
from sandwich.core.service.predicate_service import predicate_for_predicate_name

# Map a predicate name to kwargs for Entity.objects.filter
# Extend this to add support for other predicates
predicate_entity_map = {
    PredicateName.HAS_CONDITION: {"type": EntityType.CONDITION},
    PredicateName.TAKES_MEDICATION: {"type": EntityType.MEDICATION},
}


class FactFactory(factory.django.DjangoModelFactory[Fact]):
    class Meta:
        model = Fact
        skip_postgeneration_save = True

    subject = None  # must be provided
    predicate = factory.Iterator(Predicate.objects.filter(name__in=predicate_entity_map.keys()))

    @factory.lazy_attribute
    def object(self):
        filter_kwargs = {}
        if self.predicate and self.predicate.name in predicate_entity_map:  # type: ignore[attr-defined]
            filter_kwargs = predicate_entity_map[self.predicate.name]  # type: ignore[attr-defined]
        random_object = Entity.objects.filter(**filter_kwargs).order_by("?").first()
        if not random_object:
            raise FactoryError(f"No entities found {filter_kwargs=}")
        return random_object


class EntityMetadataFactory(factory.DictFactory):
    label = factory.Faker("word")


class EntityFactory(factory.django.DjangoModelFactory[Entity]):
    class Meta:
        model = Entity
        skip_postgeneration_save = True

    type = factory.Iterator(EntityType)
    metadata = factory.SubFactory(EntityMetadataFactory)


def generate_facts_for_predicate(patient: Patient, predicate_name: PredicateName, count: int) -> list[Fact]:
    return FactFactory.create_batch(
        size=count,
        subject=Entity.for_patient(patient),
        predicate=predicate_for_predicate_name(predicate_name),
    )
