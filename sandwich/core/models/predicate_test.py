import pytest

from sandwich.core.models.predicate import Predicate
from sandwich.core.models.predicate import PredicateName


@pytest.mark.django_db
def test_create_predicate_enum():
    p = Predicate.objects.create(name=PredicateName.HAS_CONDITION, description="Patient has a condition.")
    assert p.pk is not None
    assert p.name == PredicateName.HAS_CONDITION
    assert p.description == "Patient has a condition."


@pytest.mark.django_db
def test_predicate_str():
    p = Predicate.objects.create(name=PredicateName.TAKES_MEDICATION, description="Patient takes medication.")
    assert str(p) == PredicateName.TAKES_MEDICATION.value


@pytest.mark.django_db
def test_invalid_predicate_name():
    with pytest.raises(ValueError, match="'NOT_A_VALID_PREDICATE' is not a valid PredicateName"):
        PredicateName("NOT_A_VALID_PREDICATE")
