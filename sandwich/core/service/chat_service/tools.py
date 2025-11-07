from langchain_core.tools import BaseTool

from sandwich.core.models import Patient
from sandwich.core.service.tool_service.patient import build_list_patients_tool
from sandwich.core.service.tool_service.patient import build_patient_graph_tool
from sandwich.users.models import User


def get_tools(user: User | None, patient: Patient | None) -> list[BaseTool]:
    tools = []
    if user:
        tools.append(build_list_patients_tool(user))
    if user and patient:
        tools.append(build_patient_graph_tool(user, patient))
    return tools
