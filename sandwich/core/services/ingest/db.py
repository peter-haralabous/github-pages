import logging
import uuid

from dateutil.parser import isoparse
from django.utils import timezone

from sandwich.core.models import Entity
from sandwich.core.models import Fact
from sandwich.core.models import Patient
from sandwich.core.models import Predicate
from sandwich.core.models.provenance import Provenance
from sandwich.core.services.ingest.types import Triple

logger = logging.getLogger(__name__)


def stringify_uuids(obj):
    if isinstance(obj, dict):
        return {k: stringify_uuids(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [stringify_uuids(v) for v in obj]
    if isinstance(obj, uuid.UUID):
        return str(obj)
    return obj


def get_or_create_entity(object_type, object_label, node):
    node_str = stringify_uuids(node)
    # for Patient, deduplicate by patient_id if present
    if object_type == "Patient" and "patient_id" in node_str:
        entity, _ = Entity.objects.update_or_create(
            type=object_type,
            metadata__patient_id=str(node_str["patient_id"]),
            defaults={"metadata": node_str},
        )
        return entity
    # for all other types, fall back to name-based lookup
    entity, _ = Entity.objects.update_or_create(
        type=object_type,
        metadata__name=object_label,
        defaults={"metadata": node_str},
    )
    return entity


def get_or_create_predicate(predicate_name, predicate_text):
    predicate, _ = Predicate.objects.get_or_create(
        name=predicate_name,
        defaults={"description": predicate_text},
    )
    return predicate


def create_provenance(provenance_data, source_type):
    stype = provenance_data.get("source_type") if provenance_data.get("source_type") else source_type
    if stype is None:
        stype = "unknown"
    extracted_by = provenance_data.get("extracted_by") or "unknown"
    page = provenance_data.get("page")
    extracted_at = provenance_data.get("extracted_at")
    dt = None
    if extracted_at:
        try:
            dt = isoparse(extracted_at)
        except (ValueError, TypeError):
            dt = timezone.now()
    else:
        dt = timezone.now()
    provenance_kwargs = {
        "page": page,
        "extracted_by": extracted_by,
        "source_type": stype,
        "extracted_at": dt,
    }
    return Provenance.objects.create(**provenance_kwargs)


def _create_patient_if_needed(subj_node, patient=None):
    # if a patient is provided, use their id
    if patient and hasattr(patient, "id"):
        subj_node["patient_id"] = patient.id
        return patient.id
    patient_fields = {}
    patient_fields["first_name"] = subj_node.get("first_name", "")
    patient_fields["last_name"] = subj_node.get("last_name", "")
    for key in ["date_of_birth", "email", "province", "phn", "user", "organization"]:
        if key in subj_node:
            patient_fields[key] = subj_node[key]
    if "date_of_birth" not in patient_fields:
        # FIXME-RG: this is a temporary fix to deal with missing DOBs
        patient_fields["date_of_birth"] = "1900-01-01"
    patient_obj = Patient.objects.create(**patient_fields)
    subj_node["patient_id"] = patient_obj.id
    return patient_obj.id


def save_triples(
    triples: list[Triple],
    patient=None,
    source_type: str | None = None,
) -> int:
    """
    Persists triples into the database.
    Responsibilities:
    - Resolve or create subject/object entities.
    - Create patient if not provided.
    - Resolve or create predicates.
    - Create Fact records.
    """
    count = 0
    if not triples:
        return 0
    # assume all triples refer to the same patient
    # this may need to be revisited in the future
    subj = triples[0].subject
    patient_id = _create_patient_if_needed(subj.node, patient=patient)
    # inject patient_id into all subject nodes
    for t in triples:
        t.subject.node["patient_id"] = patient_id
    for t in triples:
        try:
            subj = t.subject
            obj = getattr(t, "obj", None) if hasattr(t, "obj") else getattr(t, "object", None)
            if obj is None:
                logger.warning("[save_triples] Skipping triple with no object")
                continue
            pred = t.normalized_predicate
            predicate_text = t.predicate
            subject_entity = get_or_create_entity("Patient", subj.node.get("name", ""), subj.node)
            object_type = obj.entity_type
            object_label = obj.node["name"]
            object_entity = get_or_create_entity(object_type, object_label, obj.node)
            predicate_name = pred.predicate_type
            predicate = get_or_create_predicate(predicate_name, predicate_text)
            provenance_data = t.provenance or {}
            provenance_obj = create_provenance(provenance_data, source_type)
            fact = Fact.objects.create(
                subject=subject_entity,
                predicate=predicate,
                object=object_entity,
                provenance=provenance_obj,
            )
            logger.info("[save_triples] Saved Fact: %r", fact.id)
            count += 1
        except Exception:
            logger.exception("[save_triples] Failed to save triple: %r", t)

    return count
