import pytest

from sandwich.core.factories.fact import EntityFactory
from sandwich.core.factories.fact import FactFactory
from sandwich.core.factories.fact import _entities_for_predicate
from sandwich.core.models import Entity
from sandwich.core.models import Patient
from sandwich.core.models import Predicate
from sandwich.core.models.predicate import PredicateName
from sandwich.core.service.predicate_service import predicate_for_predicate_name


@pytest.fixture
def predicate(db) -> Predicate:
    return predicate_for_predicate_name(PredicateName.HAS_FAMILY_HISTORY)


@pytest.fixture
def entity_in_use(patient: Patient, patient_entity: Entity, predicate: Predicate) -> Entity:
    return FactFactory.create(
        patient=patient,
        subject=patient_entity,
        predicate=predicate,
        object=EntityFactory.create(),
    ).object


@pytest.fixture
def entity_marked_for_use(predicate: Predicate) -> Entity:
    return EntityFactory.create(metadata={"_predicates": [predicate.name.value]})


def test__entities_for_predicate(predicate: Predicate) -> None:
    assert _entities_for_predicate(predicate).count() == 0


def test__entities_for_predicate_in_use(predicate: Predicate, entity_in_use: Entity) -> None:
    assert entity_in_use in _entities_for_predicate(predicate)


def test__entities_for_predicate_marked(predicate: Predicate, entity_marked_for_use: Entity) -> None:
    assert entity_marked_for_use in _entities_for_predicate(predicate)
