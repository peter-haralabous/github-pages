import factory
from django.db.models import Q
from django.db.models import QuerySet

from sandwich.core.factories.errors import FactoryError
from sandwich.core.models import Entity
from sandwich.core.models import Fact
from sandwich.core.models import Patient
from sandwich.core.models import Predicate
from sandwich.core.models.entity import EntityType
from sandwich.core.models.predicate import PredicateName
from sandwich.core.service.entity_service import entity_for_patient
from sandwich.core.service.predicate_service import predicate_for_predicate_name


def _entities_for_predicate(predicate: Predicate) -> QuerySet[Entity]:
    """Return all Entities that matches the predicate type."""
    marked_for_use = Q(metadata___predicates__contains=[predicate.name.value])
    already_in_use = Q(facts_as_object__predicate__name=predicate.name)
    return Entity.objects.filter(marked_for_use | already_in_use)


def _random_entity_for_predicate(predicate: Predicate) -> Entity:
    """Return a random Entity that matches the predicate type."""
    random_object = _entities_for_predicate(predicate).order_by("?").first()
    if not random_object:
        raise FactoryError(f"No entities found for predicate {predicate}")
    return random_object


class FactFactory(factory.django.DjangoModelFactory[Fact]):
    class Meta:
        model = Fact
        skip_postgeneration_save = True

    subject = None  # must be provided
    predicate = factory.Iterator(Predicate.objects.all())

    @factory.lazy_attribute
    def object(self: Fact) -> Entity:
        """Return a random Entity that matches the predicate type."""
        return _random_entity_for_predicate(self.predicate)


class EntityMetadataFactory(factory.DictFactory):
    label = factory.Faker("word")


class EntityFactory(factory.django.DjangoModelFactory[Entity]):
    class Meta:
        model = Entity
        skip_postgeneration_save = True

    type = factory.Iterator(EntityType)
    metadata = factory.SubFactory(EntityMetadataFactory)


def generate_facts_for_predicate(patient: Patient, predicate_name: PredicateName, count: int) -> list[Fact]:
    """
    Generate a number of facts for a given patient and predicate.

    This re-uses entities that are already in use with that predicate or
    are marked for use by the inclusion of the PredicateName in list Entity.metadata._predicates.

    See: _entities_for_predicate
    """
    return FactFactory.create_batch(
        patient=patient,
        size=count,
        subject=entity_for_patient(patient),
        predicate=predicate_for_predicate_name(predicate_name),
    )
