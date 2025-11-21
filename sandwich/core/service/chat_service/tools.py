from langchain_core.tools import BaseTool

from sandwich.core.models import Patient
from sandwich.core.models.health_record import HealthRecordType
from sandwich.core.service.tool_service.patient import build_read_patient_record_tool
from sandwich.core.service.tool_service.patient import build_write_patient_record_tool
from sandwich.core.service.tool_service.time import current_date_and_time
from sandwich.users.models import User


def get_tools(user: User | None, patient: Patient | None) -> list[BaseTool]:
    tools = [current_date_and_time]
    if user and patient:
        tools.extend(
            [
                build_read_patient_record_tool(user, patient),
                build_write_patient_record_tool(user, patient, HealthRecordType.CONDITION),
                build_write_patient_record_tool(user, patient, HealthRecordType.IMMUNIZATION),
                build_write_patient_record_tool(user, patient, HealthRecordType.PRACTITIONER),
            ]
        )
    return tools
