from sandwich.core.models.predicate import Predicate
from sandwich.core.models.predicate import PredicateName


def predicate_for_predicate_name(predicate_name: PredicateName) -> Predicate:
    return Predicate.objects.get_or_create(name=predicate_name)[0]
