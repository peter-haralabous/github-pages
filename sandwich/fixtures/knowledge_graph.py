import pytest

from sandwich.core.factories.fact import EntityFactory
from sandwich.core.factories.fact import FactFactory
from sandwich.core.models import Entity
from sandwich.core.models import Fact
from sandwich.core.models import Patient
from sandwich.core.models.entity import EntityType
from sandwich.core.models.predicate import PredicateName
from sandwich.core.service.entity_service import entity_for_patient
from sandwich.core.service.predicate_service import predicate_for_predicate_name


@pytest.fixture
def patient_entity(patient: Patient) -> Entity:
    return entity_for_patient(patient)


@pytest.fixture
def patient_knowledge_graph(patient: Patient, patient_entity: Entity) -> list[Fact]:
    return [
        FactFactory.create(
            patient=patient,
            subject=patient_entity,
            predicate=predicate_for_predicate_name(PredicateName.HAS_CONDITION),
            object=EntityFactory.create(type=EntityType.CONDITION),
        ),
        FactFactory.create(
            patient=patient,
            subject=patient_entity,
            predicate=predicate_for_predicate_name(PredicateName.TAKES_MEDICATION),
            object=EntityFactory.create(type=EntityType.MEDICATION),
        ),
        FactFactory.create(
            patient=patient,
            subject=patient_entity,
            predicate=predicate_for_predicate_name(PredicateName.HAS_CONDITION),
            object=EntityFactory.create(type=EntityType.OBSERVATION),
        ),
        FactFactory.create(
            patient=patient,
            subject=patient_entity,
            predicate=predicate_for_predicate_name(PredicateName.HAS_VITAL_SIGN),
            object=EntityFactory.create(type=EntityType.OBSERVATION),
        ),
        FactFactory.create(
            patient=patient,
            subject=patient_entity,
            predicate=predicate_for_predicate_name(PredicateName.HAS_SYMPTOM),
            object=EntityFactory.create(type=EntityType.CONDITION),
        ),
        FactFactory.create(
            patient=patient,
            subject=patient_entity,
            predicate=predicate_for_predicate_name(PredicateName.HAS_ALLERGY),
            object=EntityFactory.create(type=EntityType.ALLERGY_INTOLERANCE),
        ),
        # FactFactory.create(
        #     patient=patient,
        #     subject=patient_entity,
        #     predicate=predicate_for_predicate_name(PredicateName.HAS_FAMILY_HISTORY),
        #     object=EntityFactory.create(),
        # ),
        FactFactory.create(
            patient=patient,
            subject=patient_entity,
            predicate=predicate_for_predicate_name(PredicateName.RECEIVED_IMMUNIZATION),
            object=EntityFactory.create(type=EntityType.IMMUNIZATION),
        ),
        FactFactory.create(
            patient=patient,
            subject=patient_entity,
            predicate=predicate_for_predicate_name(PredicateName.UNDERWENT_PROCEDURE),
            object=EntityFactory.create(type=EntityType.PROCEDURE),
        ),
    ]
