from langchain_core.tools import BaseTool

from sandwich.core.models import Patient
from sandwich.core.service.tool_service.patient import build_read_patient_record_tool
from sandwich.users.models import User


def get_tools(user: User | None, patient: Patient | None) -> list[BaseTool]:
    tools = []
    if user and patient:
        tools.append(build_read_patient_record_tool(user, patient))
    return tools
