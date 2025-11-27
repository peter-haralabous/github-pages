import datetime
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from sandwich.core.models import Condition
from sandwich.core.models import Document
from sandwich.core.models import Immunization
from sandwich.core.models import Patient
from sandwich.core.models import Practitioner
from sandwich.core.models.condition import ConditionStatus
from sandwich.core.models.health_record import HealthRecordType
from sandwich.core.service.llm import ModelName
from sandwich.core.service.tool_service.patient import build_read_patient_record_tool
from sandwich.core.service.tool_service.patient import build_update_patient_record_tool
from sandwich.core.service.tool_service.patient import build_write_patient_record_tool
from sandwich.users.models import User

if TYPE_CHECKING:
    from langchain_core.tools import StructuredTool

    from sandwich.core.service.tool_service.types import ModelDict


@pytest.fixture
def patient_record_query_tool(user: User, patient: Patient) -> "StructuredTool":
    return build_read_patient_record_tool(user, patient)


@pytest.fixture
def tool_runtime() -> "MagicMock":
    mock = MagicMock()
    mock.context.llm = ModelName.DEFAULT
    mock.config = {"configurable": {"thread_id": "test-thread-id"}}
    return mock


def test_patient_record_tool_condition(
    patient_record_query_tool: "StructuredTool",
    condition: Condition,
    other_condition: Condition,
):
    object_ = (condition._meta.label_lower, str(condition.pk))  # noqa: SLF001
    other_object = (other_condition._meta.label_lower, str(other_condition.pk))  # noqa: SLF001
    results = patient_record_query_tool.func(types=[HealthRecordType.CONDITION])  # type: ignore[misc]

    objects = {(r["model"], r["pk"]) for r in results}
    assert object_ in objects
    assert other_object not in objects


def test_patient_record_tool_document(
    patient_record_query_tool: "StructuredTool",
    document: Document,
    other_document: Document,
):
    object_ = (document._meta.label_lower, str(document.pk))  # noqa: SLF001
    other_object = (other_document._meta.label_lower, str(other_document.pk))  # noqa: SLF001
    results = patient_record_query_tool.func(types=[HealthRecordType.DOCUMENT])  # type: ignore[misc]

    objects = {(r["model"], r["pk"]) for r in results}
    assert object_ in objects
    assert other_object not in objects


def test_patient_record_tool_immunization(
    patient_record_query_tool: "StructuredTool",
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
    patient_record_query_tool: "StructuredTool",
    practitioner: Practitioner,
    other_practitioner: Practitioner,
):
    object_ = (practitioner._meta.label_lower, str(practitioner.pk))  # noqa: SLF001
    other_object = (other_practitioner._meta.label_lower, str(other_practitioner.pk))  # noqa: SLF001
    results = patient_record_query_tool.func(types=[HealthRecordType.PRACTITIONER])  # type: ignore[misc]

    objects = {(r["model"], r["pk"]) for r in results}
    assert object_ in objects
    assert other_object not in objects


def test_create_condition_tool(
    user: User,
    patient: Patient,
    tool_runtime: MagicMock,
):
    tool: StructuredTool = build_write_patient_record_tool(user, patient, HealthRecordType.CONDITION)
    result: ModelDict = tool.func(
        name="Name", status=ConditionStatus.ACTIVE, onset=datetime.date(1999, 12, 31), runtime=tool_runtime
    )  # type: ignore[misc]
    condition = Condition.objects.get(pk=result["pk"])
    assert condition.get_current_version().pgh_context.metadata == {
        "conversation": "test-thread-id",
        "llm": ModelName.DEFAULT.value,
    }

    assert condition.patient == patient
    assert condition.encounter is None
    assert condition.name == "Name"
    assert condition.onset == datetime.date(1999, 12, 31)
    assert condition.abatement is None
    assert condition.status == ConditionStatus.ACTIVE


def test_update_condition_tool(
    user: User,
    patient: Patient,
    condition: Condition,
    tool_runtime: MagicMock,
):
    tool: StructuredTool = build_update_patient_record_tool(user, patient, HealthRecordType.CONDITION)
    result: ModelDict = tool.func(
        pk=str(condition.pk),
        name="New Name",
        status=ConditionStatus.RESOLVED,
        onset=datetime.date(1999, 12, 31),
        abatement=datetime.date(2020, 1, 1),
        runtime=tool_runtime,
    )  # type: ignore[misc]
    condition = Condition.objects.get(pk=result["pk"])
    assert condition.get_current_version().pgh_context.metadata == {
        "conversation": "test-thread-id",
        "llm": ModelName.DEFAULT.value,
    }

    assert condition.patient == patient
    assert condition.name == "New Name"
    assert condition.onset == datetime.date(1999, 12, 31)
    assert condition.abatement == datetime.date(2020, 1, 1)
    assert condition.status == ConditionStatus.RESOLVED


def test_create_immunization_tool(
    user: User,
    patient: Patient,
    tool_runtime: MagicMock,
):
    tool: StructuredTool = build_write_patient_record_tool(user, patient, HealthRecordType.IMMUNIZATION)
    result: ModelDict = tool.func(name="Name", date=datetime.date(1999, 12, 31), runtime=tool_runtime)  # type: ignore[misc]
    immunization = Immunization.objects.get(pk=result["pk"])
    assert immunization.get_current_version().pgh_context.metadata == {
        "conversation": "test-thread-id",
        "llm": ModelName.DEFAULT.value,
    }

    assert immunization.patient == patient
    assert immunization.encounter is None
    assert immunization.name == "Name"
    assert immunization.date == datetime.date(1999, 12, 31)


def test_update_immunization_tool(
    user: User,
    patient: Patient,
    immunization: Immunization,
    tool_runtime: MagicMock,
):
    tool: StructuredTool = build_update_patient_record_tool(user, patient, HealthRecordType.IMMUNIZATION)
    result: ModelDict = tool.func(
        pk=str(immunization.pk), name="New Name", date=datetime.date(2000, 12, 31), runtime=tool_runtime
    )  # type: ignore[misc]
    immunization = Immunization.objects.get(pk=result["pk"])
    assert immunization.get_current_version().pgh_context.metadata == {
        "conversation": "test-thread-id",
        "llm": ModelName.DEFAULT.value,
    }

    assert immunization.patient == patient
    assert immunization.name == "New Name"
    assert immunization.date == datetime.date(2000, 12, 31)


def test_create_practitioner_tool(
    user: User,
    patient: Patient,
    tool_runtime: MagicMock,
):
    tool: StructuredTool = build_write_patient_record_tool(user, patient, HealthRecordType.PRACTITIONER)
    result: ModelDict = tool.func(name="Name", runtime=tool_runtime)  # type: ignore[misc]
    practitioner = Practitioner.objects.get(pk=result["pk"])
    assert practitioner.get_current_version().pgh_context.metadata == {
        "conversation": "test-thread-id",
        "llm": ModelName.DEFAULT.value,
    }

    assert practitioner.patient == patient
    assert practitioner.encounter is None
    assert practitioner.name == "Name"


def test_update_practitioner_tool(
    user: User,
    patient: Patient,
    practitioner: Practitioner,
    tool_runtime: MagicMock,
):
    tool: StructuredTool = build_update_patient_record_tool(user, patient, HealthRecordType.PRACTITIONER)
    result: ModelDict = tool.func(pk=str(practitioner.pk), name="New Name", runtime=tool_runtime)  # type: ignore[misc]
    practitioner = Practitioner.objects.get(pk=result["pk"])
    assert practitioner.get_current_version().pgh_context.metadata == {
        "conversation": "test-thread-id",
        "llm": ModelName.DEFAULT.value,
    }

    assert practitioner.patient == patient
    assert practitioner.name == "New Name"
