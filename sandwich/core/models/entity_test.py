import pytest
from django.db import IntegrityError
from django.db import transaction

from sandwich.core.models import Entity
from sandwich.core.models.entity import EntityType
from sandwich.core.models.patient import Patient


@pytest.mark.django_db
def test_entity_unique_patient_fk():
    # FK-based uniqueness: only one Entity of type Patient may reference a given Patient
    p1 = Patient.objects.create(first_name="Jane", last_name="Doe", date_of_birth="2000-01-01")
    p2 = Patient.objects.create(first_name="John", last_name="Smith", date_of_birth="1990-01-01")

    e1 = Entity.objects.create(type=EntityType.PATIENT, patient=p1)
    assert e1.pk is not None

    # Creating another entity that references the same Patient should violate the unique constraint
    with pytest.raises(IntegrityError), transaction.atomic():
        Entity.objects.create(type=EntityType.PATIENT, patient=p1)

    # Different patient is allowed
    e2 = Entity.objects.create(type=EntityType.PATIENT, patient=p2)
    assert e2.pk is not None


@pytest.mark.django_db
def test_entity_non_patient_patient_fk_allowed():
    # Non-Patient entities: patient_id can be duplicated
    # Although this probably won't occur in practice,
    # we want to ensure that the constraint only applies to Patient entities.
    p = Patient.objects.create(first_name="Alice", last_name="Jones", date_of_birth="1985-05-05")

    e1 = Entity.objects.create(type=EntityType.CONDITION, patient=p)
    e2 = Entity.objects.create(type=EntityType.CONDITION, patient=p)
    assert e1.pk is not None
    assert e2.pk is not None

    e3 = Entity.objects.create(type=EntityType.MEDICATION, patient=p)
    e4 = Entity.objects.create(type=EntityType.MEDICATION, patient=p)
    assert e3.pk is not None
    assert e4.pk is not None


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


@pytest.mark.django_db
def test_patient_entity_deleted_when_patient_deleted():
    # Create a patient and its associated patient Entity
    p = Patient.objects.create(first_name="Jane", last_name="Doe", date_of_birth="1992-02-02")
    ent = Entity.objects.create(type=EntityType.PATIENT, patient=p)
    assert ent.pk is not None

    # Deleting the patient should remove the associated Entity via cascade
    p.delete()
    assert not Entity.objects.filter(pk=ent.pk).exists()
