import dataclasses
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any
from typing import Unpack

from langchain.agents.structured_output import ToolStrategy
from langgraph.graph.state import CompiledStateGraph

from sandwich.core.models import Patient
from sandwich.core.service.agent_service.agent import AgentParameters
from sandwich.core.service.agent_service.agent import thrive_agent
from sandwich.core.service.chat_service.response import ChatResponse
from sandwich.core.service.chat_service.tools import get_tools
from sandwich.core.service.llm import ModelName
from sandwich.core.service.llm import get_llm
from sandwich.core.service.prompt_service.chat import chat_template
from sandwich.core.service.prompt_service.chat import patient_context
from sandwich.core.service.prompt_service.chat import user_context
from sandwich.users.models import User

LLM_MODEL = ModelName.DEFAULT


@dataclasses.dataclass
class ChatAgentContext:
    llm: ModelName = LLM_MODEL


@contextmanager
def chat_agent(
    user: User | None = None,
    patient: Patient | None = None,
    **params: Unpack[AgentParameters],
) -> Generator[CompiledStateGraph, Any, None]:
    response_format = ToolStrategy(ChatResponse)
    system_prompt = chat_template.format(
        user_context=user_context(user) if user else "No User for context",
        patient_context=patient_context(patient) if patient else "No Patient for context",
    )
    params.setdefault("tools", get_tools(user, patient))
    params["model"] = get_llm(LLM_MODEL)
    params["context_schema"] = ChatAgentContext

    with thrive_agent(
        name="patient_chat_agent",
        system_prompt=system_prompt,
        response_format=response_format,
        **params,
    ) as agent:
        yield agent
