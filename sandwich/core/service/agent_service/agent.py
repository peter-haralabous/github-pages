from collections.abc import Generator
from contextlib import contextmanager
from typing import Any
from typing import TypedDict
from typing import Unpack

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.store.base import BaseStore

from sandwich.core.service.agent_service.memory import checkpointer_context
from sandwich.core.service.agent_service.memory import store_context
from sandwich.core.service.agent_service.middleware import close_db_connections
from sandwich.core.service.agent_service.middleware import exception_handling
from sandwich.core.service.llm import ModelName
from sandwich.core.service.llm import get_llm
from sandwich.core.service.prompt_service.template import template_contents


class AgentParameters(TypedDict, total=False):
    model: BaseChatModel | None
    tools: list[BaseTool] | None
    checkpointer: BaseCheckpointSaver | None
    store: BaseStore | None
    context_schema: object | None


class ResponseMessage[T](TypedDict):
    """The return value from agent.invoke when used with_structured_output

    See BaseChatModel.with_structured_output(include_raw=True)
    """

    raw: BaseMessage
    parsed: T | None
    parsing_error: str | None


@contextmanager
def thrive_agent(
    name: str,
    response_format: ToolStrategy | None = None,
    system_prompt: str | None = None,
    **params: Unpack[AgentParameters],
) -> Generator[CompiledStateGraph, Any, None]:
    """
    A thin wrapper around langchain's create_agent that also manages checkpointer and store contexts.

    Usage:

    with thrive_agent(name="my_agent") as agent:
        agent.invoke({"messages": [...]"})
    """
    system_prompt = system_prompt or template_contents("system.md")

    with (
        checkpointer_context(existing_checkpointer=params.get("checkpointer")) as checkpointer,
        store_context(existing_store=params.get("store")) as store,
    ):
        yield create_agent(
            name=name,
            model=params.get("model") or get_llm(ModelName.DEFAULT),
            tools=params.get("tools"),
            system_prompt=system_prompt,
            response_format=response_format,
            checkpointer=checkpointer,
            store=store,
            middleware=[close_db_connections, exception_handling],
        )
