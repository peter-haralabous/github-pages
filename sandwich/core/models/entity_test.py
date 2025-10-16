import pytest
from django.db import IntegrityError
from django.db import transaction

from sandwich.core.models import Entity
from sandwich.core.models.entity import EntityType


@pytest.mark.django_db
def test_entity_unique_patient_id():
    # Create a Patient entity with patient_id in metadata
    e1 = Entity.objects.create(type=EntityType.PATIENT, metadata={"patient_id": "abc"})
    assert e1.pk is not None

    # Creating another Patient entity with the same patient_id should fail
    with pytest.raises(IntegrityError), transaction.atomic():
        Entity.objects.create(type=EntityType.PATIENT, metadata={"patient_id": "abc"})

    # Creating another Patient entity with a different patient_id should succeed
    e2 = Entity.objects.create(type=EntityType.PATIENT, metadata={"patient_id": "def"})
    assert e2.pk is not None

    # Creating a Patient entity without patient_id in metadata should succeed
    e3 = Entity.objects.create(type=EntityType.PATIENT, metadata={})
    assert e3.pk is not None


@pytest.mark.django_db
def test_entity_type_enum():
    e_patient = Entity.objects.create(type=EntityType.PATIENT, metadata={})
    e_condition = Entity.objects.create(type=EntityType.CONDITION, metadata={})
    e_medication = Entity.objects.create(type=EntityType.MEDICATION, metadata={})
    e_observation = Entity.objects.create(type=EntityType.OBSERVATION, metadata={})
    assert e_patient.type == EntityType.PATIENT
    assert e_condition.type == EntityType.CONDITION
    assert e_medication.type == EntityType.MEDICATION
    assert e_observation.type == EntityType.OBSERVATION
