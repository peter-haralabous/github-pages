from typing import Annotated
from typing import Any
from typing import cast

import pghistory
from django.core.serializers.python import Serializer as PythonSerializer
from guardian.shortcuts import get_objects_for_user
from langchain_core.tools import BaseTool
from langchain_core.tools import StructuredTool
from langchain_core.tools import tool
from langgraph.prebuilt import ToolRuntime
from pydantic import ConfigDict

from sandwich.core.models import Condition
from sandwich.core.models import Document
from sandwich.core.models import Fact
from sandwich.core.models import Immunization
from sandwich.core.models import Patient
from sandwich.core.models import Practitioner
from sandwich.core.models.health_record import HealthRecordType
from sandwich.core.service.llm import ModelName
from sandwich.core.service.tool_service.response import ErrorResponse
from sandwich.core.service.tool_service.types import ModelDict  # noqa: TC001
from sandwich.users.models import User


def build_list_patients_tool(user: User) -> BaseTool:
    """Build a tool that can list all patients visible to the user."""

    @tool(description=f"A list of patients that {user.get_full_name()} can manage")
    def list_patients() -> str:
        patients = get_objects_for_user(user, "view_patient", Patient)
        if patients:
            return "\n".join([f"- {patient.full_name} (ID: {patient.id})" for patient in patients])
        return "No patients found."

    return list_patients


def build_patient_graph_tool(user: User, patient: Patient) -> BaseTool:
    """Build a tool that can present the patient graph visible to the user."""

    @tool(
        "read_medical_facts",
        description=f"Describes medical facts about {patient.full_name}",
    )
    def medical_facts() -> str:
        facts = get_objects_for_user(user, "view_fact", Fact).filter(subject__patient=patient)
        if facts:
            return "\n".join([f"- {fact.predicate.name} {fact.object} ({fact.object.type})" for fact in facts])
        return "No medical facts found."

    return medical_facts


def build_read_patient_record_tool(user: User, patient: Patient) -> "StructuredTool":
    """Build a tool that can present the patient's medical record visible to the user."""

    serializer = PythonSerializer()

    type_queryset_map = {
        HealthRecordType.CONDITION: Condition.objects.filter(patient=patient),
        HealthRecordType.DOCUMENT: Document.objects.filter(patient=patient),
        HealthRecordType.IMMUNIZATION: Immunization.objects.filter(patient=patient),
        HealthRecordType.PRACTITIONER: Practitioner.objects.filter(patient=patient),
    }

    @tool(
        "read_medical_record",
        description=f"Retrieve medical records for {patient.full_name}",
    )
    def medical_record(types: list[HealthRecordType]) -> "list[ModelDict]":
        records = []

        for health_record_type, queryset in type_queryset_map.items():
            if health_record_type in types:
                records.extend(serializer.serialize(queryset=queryset))
        return records

    return cast("StructuredTool", medical_record)


def build_write_patient_record_tool(user: User, patient: Patient, type_: HealthRecordType) -> StructuredTool:
    """Build a tool that can write to the patient's medical record"""
    from sandwich.patients.views.patient.health_records import _form_class  # noqa: PLC0415

    form_class = _form_class(type_)

    class ExtendedSchema(form_class.pydantic_schema()):  # type: ignore[misc]
        model_config = ConfigDict(arbitrary_types_allowed=True)

        runtime: ToolRuntime

    @tool(
        f"write_{type_.value.lower()}_record",
        description=f"Create {type_} records for {patient.full_name}",
        args_schema=ExtendedSchema,
    )
    def write_patient_record(runtime: ToolRuntime, **kwargs) -> "ModelDict | ErrorResponse":
        form = form_class(data=kwargs)
        if form.is_valid():
            with pghistory.context(
                llm=runtime.context.llm.value,  # type: ignore[attr-defined]
                conversation=runtime.config["configurable"]["thread_id"],
            ):
                obj = form.save(patient=patient, commit=False)
                obj.unattested = True  # The tool is making the update on behalf of the user.
                obj.save()
                return PythonSerializer().serialize([obj])[0]
        return ErrorResponse(errors=form.errors)

    return cast("StructuredTool", write_patient_record)


def build_update_patient_record_tool(user: User, patient: Patient, type_: HealthRecordType) -> StructuredTool:
    """Build a tool that can edit the patient's medical record"""
    from sandwich.patients.views.patient.health_records import _form_class  # noqa: PLC0415

    form_class = _form_class(type_)
    model_class = form_class._meta.model  # noqa: SLF001

    class ExtendedSchema(form_class.pydantic_schema()):  # type: ignore[misc]
        model_config = ConfigDict(arbitrary_types_allowed=True)

        runtime: ToolRuntime
        pk: Annotated[str, "The primary key of the record to update"]

    @tool(
        f"update_{type_.value.lower()}_record",
        description=f"Update {type_} records for {patient.full_name}",
        args_schema=ExtendedSchema,
    )
    def update_patient_record(pk: str, runtime: ToolRuntime, **kwargs) -> dict[str, Any]:
        instance = model_class.objects.get(pk=pk, patient=patient)
        form = form_class(data=kwargs, instance=instance)
        if form.is_valid():
            with pghistory.context(
                llm=runtime.context.llm.value,  # type: ignore[attr-defined]
                conversation=runtime.config["configurable"]["thread_id"],
            ):
                obj = form.save(patient=patient)
            return PythonSerializer().serialize([obj])[0]
        return {"errors": form.errors}

    return cast("StructuredTool", update_patient_record)
