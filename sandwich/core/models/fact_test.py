import pytest

from sandwich.core.factories.fact import EntityFactory
from sandwich.core.models import Entity
from sandwich.core.models import Fact
from sandwich.core.models import Patient
from sandwich.core.models.entity import EntityType
from sandwich.core.models.predicate import Predicate
from sandwich.core.models.predicate import PredicateName
from sandwich.core.service.predicate_service import predicate_for_predicate_name


@pytest.fixture
def non_patient_subject() -> Entity:
    return EntityFactory.create(type=EntityType.CONDITION)


@pytest.fixture
def arbitrary_predicate() -> Predicate:
    return predicate_for_predicate_name(PredicateName.HAS_ALLERGY)


@pytest.fixture
def arbitrary_object() -> Entity:
    return EntityFactory.create(type=EntityType.MEDICATION)


def test_fact_no_patient(
    db, non_patient_subject: Entity, arbitrary_predicate: Predicate, arbitrary_object: Entity
) -> None:
    assert (
        Fact.objects.create(
            patient=None,  # type: ignore[misc]
            subject=non_patient_subject,
            predicate=arbitrary_predicate,
            object=arbitrary_object,
        )
        is not None
    )


def test_fact_patient(
    db, patient: Patient, patient_entity: Entity, arbitrary_predicate: Predicate, arbitrary_object: Entity
) -> None:
    fact = Fact.objects.create(
        patient=patient,  # type: ignore[misc]
        subject=patient_entity,
        predicate=arbitrary_predicate,
        object=arbitrary_object,
    )
    assert fact is not None
    assert patient.user is not None
    assert patient.user.has_perm("view_fact", fact)
    assert patient.user.has_perm("change_fact", fact)


def test_fact_patient_omitted(
    db, patient: Patient, patient_entity: Entity, arbitrary_predicate: Predicate, arbitrary_object: Entity
) -> None:
    with pytest.raises(ValueError, match="Patient must be provided"):
        Fact.objects.create(
            subject=patient_entity,
            predicate=arbitrary_predicate,
            object=arbitrary_object,
        )
