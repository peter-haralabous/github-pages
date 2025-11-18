"""Health Summary Service - Generate AI summaries of patient health records."""

import logging

from langchain.agents.structured_output import ToolStrategy
from pydantic import BaseModel

from sandwich.core.models import Patient
from sandwich.core.service.agent_service.agent import thrive_agent
from sandwich.core.service.prompt_service.chat import patient_summary_system

logger = logging.getLogger(__name__)


class OutputSchema(BaseModel):
    content: str
    """Markdown formatted output of health summary."""


def generate_health_summary(patient: Patient) -> str:
    prompt = patient_summary_system(patient)
    with thrive_agent(
        "patient_summary_agent",
        system_prompt=prompt,
        response_format=ToolStrategy(OutputSchema),
    ) as agent:
        response = agent.invoke(
            {"messages": [{"role": "user", "content": "Create a summary"}]},
            config={"configurable": {"thread_id": f"summary-{patient.id}"}},
        )["structured_response"]

        return response.content
