from typing import Any
from typing import Literal

from django.core import serializers
from django.utils.text import slugify
from guardian.shortcuts import get_objects_for_user
from langchain_core.tools import BaseTool
from langchain_core.tools import tool

from sandwich.core.models import Condition
from sandwich.core.models import Fact
from sandwich.core.models import Immunization
from sandwich.core.models import Patient
from sandwich.core.models import Practitioner
from sandwich.users.models import User


def _patient_fn_slug(patient: Patient):
    """Generate a slug of the patient's name that is suitable for inclusion in tool function names."""
    return slugify(patient.full_name).replace("-", "_")


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
        f"{_patient_fn_slug(patient)}_medical_facts",
        description=f"Describes medical facts about {patient.full_name}",
    )
    def medical_facts() -> str:
        facts = get_objects_for_user(user, "view_fact", Fact).filter(subject__patient=patient)
        if facts:
            return "\n".join([f"- {fact.predicate.name} {fact.object} ({fact.object.type})" for fact in facts])
        return "No medical facts found."

    return medical_facts


def build_patient_record_tool(user: User, patient: Patient) -> BaseTool:
    """Build a tool that can present the patient's medical record visible to the user."""

    @tool(
        f"{_patient_fn_slug(patient)}_medical_record",
        description=f"Access medical records for {patient.full_name}",
    )
    def medical_record(types: list[Literal["conditions", "immunizations", "practitioners"]]) -> list[dict[str, Any]]:
        records = []

        if "conditions" in types:
            records.extend(
                serializers.serialize(
                    format="json",
                    queryset=Condition.objects.filter(patient=patient),
                )
            )
        if "immunizations" in types:
            records.extend(
                serializers.serialize(
                    format="json",
                    queryset=Immunization.objects.filter(patient=patient),
                )
            )
        if "practitioners" in types:
            records.extend(
                serializers.serialize(
                    format="json",
                    queryset=Practitioner.objects.filter(patient=patient),
                )
            )
        return records

    return medical_record
