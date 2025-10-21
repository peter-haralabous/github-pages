import uuid

import pytest

from sandwich.core.models import Entity
from sandwich.core.models import Fact
from sandwich.core.models import Patient
from sandwich.core.models.entity import EntityType
from sandwich.core.services.ingest import db
from sandwich.core.services.ingest.types import Entity as TripleEntity
from sandwich.core.services.ingest.types import NormalizedPredicate
from sandwich.core.services.ingest.types import Triple


@pytest.mark.django_db
def test_stringify_uuids_simple():
    u = uuid.uuid4()
    result = db.stringify_uuids(u)
    assert isinstance(result, str)
    assert result == str(u)


@pytest.mark.django_db
def test_stringify_uuids_dict():
    u = uuid.uuid4()
    d = {"foo": u, "bar": 123}
    result = db.stringify_uuids(d)
    assert result["foo"] == str(u)
    assert result["bar"] == 123


@pytest.mark.django_db
def test_stringify_uuids_list():
    u1 = uuid.uuid4()
    u2 = uuid.uuid4()
    lst = [u1, {"nested": u2}]
    result = db.stringify_uuids(lst)
    assert result[0] == str(u1)
    assert result[1]["nested"] == str(u2)


@pytest.mark.django_db
def test_stringify_uuids_nested():
    u = uuid.uuid4()
    data = {"a": [u, {"b": u}]}
    result = db.stringify_uuids(data)
    assert result["a"][0] == str(u)
    assert result["a"][1]["b"] == str(u)


@pytest.fixture
def triple_factory():
    def _make_triple(first_name="Jane", last_name="Doe", obs_name="Fever"):
        subj = TripleEntity(entityType="Patient", node={"first_name": first_name, "last_name": last_name})
        obj = TripleEntity(entityType="Observation", node={"name": obs_name})
        pred = NormalizedPredicate(predicateType="HAS_SYMPTOM", traits=None, properties={})
        return Triple(subject=subj, predicate="has a symptom", normalizedPredicate=pred, object=obj, provenance=None)

    return _make_triple


@pytest.mark.django_db
def test_save_triples_creates_patient_and_fact():
    subj = TripleEntity(entityType="Patient", node={"first_name": "Jane", "last_name": "Doe"})
    obj = TripleEntity(entityType="Observation", node={"name": "Fever"})
    pred = NormalizedPredicate(predicateType="HAS_SYMPTOM", traits=None, properties={})
    triple = Triple(subject=subj, predicate="has a symptom", normalizedPredicate=pred, object=obj, provenance=None)

    count = db.save_triples([triple])
    assert count == 1
    assert Patient.objects.count() == 1
    assert Fact.objects.count() == 1
    assert Entity.objects.filter(type=EntityType.PATIENT.value).count() == 1
    assert Entity.objects.filter(type=EntityType.OBSERVATION.value).count() == 1


@pytest.mark.django_db
def test_save_triples_with_provided_patient():
    # Create a patient up front
    patient = Patient.objects.create(first_name="Jane", last_name="Doe", date_of_birth="1980-01-01")
    subj = TripleEntity(entityType="Patient", node={"first_name": "Jane", "last_name": "Doe"})
    obj = TripleEntity(entityType="Observation", node={"name": "Cough"})
    pred = NormalizedPredicate(predicateType="HAS_SYMPTOM", traits=None, properties={})
    triple = Triple(subject=subj, predicate="has a symptom", normalizedPredicate=pred, object=obj, provenance=None)

    count = db.save_triples([triple], patient=patient)
    assert count == 1
    # Should not create a new patient
    assert Patient.objects.count() == 1
    assert Fact.objects.count() == 1
    assert Entity.objects.filter(type=EntityType.PATIENT.value).count() == 1
    assert Entity.objects.filter(type=EntityType.OBSERVATION.value).count() == 1
    # The triple's subject node should have the correct patient_id
    assert subj.node["patient_id"] == patient.id


@pytest.mark.django_db
def test_save_triples_reuses_existing_object_entity(triple_factory):
    patient = Patient.objects.create(first_name="Jane", last_name="Doe", date_of_birth="1980-01-01")
    # Create an Entity for the Observation object (use metadata field)
    obs_name = "Headache"
    observation_entity = Entity.objects.create(type=EntityType.OBSERVATION, metadata={"name": obs_name})

    # Create a triple with the same observation info
    triple = triple_factory(first_name="Jane", last_name="Doe", obs_name=obs_name)
    count = db.save_triples([triple], patient=patient)
    assert count == 1
    # Should create only one patient and reuse the observation entity
    assert Patient.objects.count() == 1
    assert Entity.objects.filter(type=EntityType.OBSERVATION.value).count() == 1
    # The triple's object node should not create a new entity
    fact = Fact.objects.first()
    assert fact is not None
    assert fact.object_id == observation_entity.id


@pytest.mark.django_db
def test_save_triples_with_provenance(triple_factory):
    patient = Patient.objects.create(first_name="Jane", last_name="Doe", date_of_birth="1980-01-01")

    # Add provenance to the triple
    provenance = {"source_type": "pdf", "extracted_by": "claude", "timestamp": "2025-10-21T12:00:00Z"}
    triple = triple_factory(first_name="Jane", last_name="Doe", obs_name="Fever")
    triple.provenance = provenance
    count = db.save_triples([triple], patient=patient)
    assert count == 1
    fact = Fact.objects.first()
    assert fact is not None
    assert fact.provenance is not None
    assert fact.provenance.source_type == provenance["source_type"]
    assert fact.provenance.extracted_by == provenance["extracted_by"]
