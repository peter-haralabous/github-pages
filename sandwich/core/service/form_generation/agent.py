from collections.abc import Generator
from contextlib import contextmanager
from typing import Any
from typing import Unpack

from langchain.agents.structured_output import ToolStrategy
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel
from pydantic import Field

from sandwich.core.service.agent_service.agent import AgentParameters
from sandwich.core.service.agent_service.agent import thrive_agent
from sandwich.core.service.form_generation.prompt import system_prompt


class SurveyElements(BaseModel):
    elements: list[dict[str, Any]] = Field(description="List of SurveyJS form elements.")


@contextmanager
def form_gen_agent(
    **params: Unpack[AgentParameters],
) -> Generator[CompiledStateGraph, Any, None]:
    from sandwich.core.service.form_generation.generate_form import SurveySchema  # noqa: PLC0415

    # TODO(MM): This should just return an array of elements
    response_format = ToolStrategy(SurveySchema)

    # We don't need to persist form generation history in the db
    checkpointer = InMemorySaver()
    params.setdefault("checkpointer", checkpointer)

    with thrive_agent(
        name="form_gen_agent",
        system_prompt=system_prompt,
        response_format=response_format,
        **params,
    ) as agent:
        yield agent
