import pytest
from langchain_core.tools import StructuredTool

from sandwich.core.models import Condition
from sandwich.core.models import Immunization
from sandwich.core.models import Patient
from sandwich.core.models import Practitioner
from sandwich.core.models.health_record import HealthRecordType
from sandwich.core.service.tool_service.patient import build_patient_record_tool
from sandwich.users.models import User


@pytest.fixture
def patient_record_query_tool(user: User, patient: Patient):
    return build_patient_record_tool(user, patient)


def test_patient_record_tool_condition(
    patient_record_query_tool: StructuredTool,
    condition: Condition,
    other_condition: Condition,
):
    object_ = (condition._meta.label_lower, str(condition.pk))  # noqa: SLF001
    other_object = (other_condition._meta.label_lower, str(other_condition.pk))  # noqa: SLF001
    results = patient_record_query_tool.func(types=[HealthRecordType.CONDITION])  # type: ignore[misc]

    objects = {(r["model"], r["pk"]) for r in results}
    assert object_ in objects
    assert other_object not in objects


def test_patient_record_tool_immunization(
    patient_record_query_tool: StructuredTool,
    immunization: Immunization,
    other_immunization: Immunization,
):
    object_ = (immunization._meta.label_lower, str(immunization.pk))  # noqa: SLF001
    other_object = (other_immunization._meta.label_lower, str(other_immunization.pk))  # noqa: SLF001
    results = patient_record_query_tool.func(types=[HealthRecordType.IMMUNIZATION])  # type: ignore[misc]

    objects = {(r["model"], r["pk"]) for r in results}
    assert object_ in objects
    assert other_object not in objects


def test_patient_record_tool_practitioner(
    patient_record_query_tool: StructuredTool,
    practitioner: Practitioner,
    other_practitioner: Practitioner,
):
    object_ = (practitioner._meta.label_lower, str(practitioner.pk))  # noqa: SLF001
    other_object = (other_practitioner._meta.label_lower, str(other_practitioner.pk))  # noqa: SLF001
    results = patient_record_query_tool.func(types=[HealthRecordType.PRACTITIONER])  # type: ignore[misc]

    objects = {(r["model"], r["pk"]) for r in results}
    assert object_ in objects
    assert other_object not in objects
