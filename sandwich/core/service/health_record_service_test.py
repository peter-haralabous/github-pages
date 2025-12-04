from sandwich.core.models import Condition
from sandwich.core.models import Document
from sandwich.core.models import Patient
from sandwich.core.models import Practitioner
from sandwich.core.models.document import DocumentCategory
from sandwich.core.service.health_record_service import get_document_count_by_category
from sandwich.core.service.health_record_service import get_health_record_count_by_type


def test_get_health_record_count_by_type(patient: Patient):
    Condition.objects.create(patient=patient)
    Practitioner.objects.create(patient=patient)
    Practitioner.objects.create(patient=patient)

    count = get_health_record_count_by_type(patient)
    assert count["condition"] == 1
    assert count["practitioner"] == 2


def test_get_document_count_by_category(patient: Patient):
    Document.objects.create(patient=patient, category=DocumentCategory.OTHER)
    Document.objects.create(patient=patient, category=DocumentCategory.IMMUNIZATIONS)
    Document.objects.create(patient=patient, category=DocumentCategory.IMMUNIZATIONS)

    assert get_document_count_by_category(patient) == {"other": 1, "immunizations": 2}
