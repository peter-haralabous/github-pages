from django.db.models import Count

from sandwich.core.models import Document
from sandwich.core.models import Patient


def get_total_health_record_count(patient: Patient) -> int:
    return patient.condition_set.count() + patient.immunization_set.count() + patient.practitioner_set.count()


def get_health_record_count_by_type(patient: Patient) -> dict[str, int]:
    # TODO: do this in a single query
    return {
        "condition": patient.condition_set.count(),
        "immunization": patient.immunization_set.count(),
        "practitioner": patient.practitioner_set.count(),
    }


def get_document_count_by_category(patient: Patient) -> dict[str, int]:
    rows = Document.objects.filter(patient=patient).values("category").annotate(count=Count("id"))
    return {row["category"]: row["count"] for row in rows}
