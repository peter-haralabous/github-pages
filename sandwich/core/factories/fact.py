import factory

from sandwich.core.models import Entity
from sandwich.core.models import Fact
from sandwich.core.models import Predicate
from sandwich.core.models.entity import EntityType
from sandwich.core.models.predicate import PredicateName

# Map a predicate name to kwargs for Entity.objects.filter
# Extend this to add support for other predicates
predicate_entity_map = {
    PredicateName.HAS_CONDITION: {"type": EntityType.CONDITION},
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
        return Entity.objects.filter(**filter_kwargs).order_by("?").first()
