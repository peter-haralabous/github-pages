import uuid
from collections.abc import Generator
from contextlib import contextmanager
from email.utils import format_datetime
from typing import TYPE_CHECKING
from typing import Any
from typing import Unpack

from django.conf import settings
from django.utils import timezone
from langchain_core.messages import AIMessage
from langchain_core.messages import ToolMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.base import BaseStore
from langgraph.store.postgres import PostgresStore

from sandwich.core.models.langgraph import CheckpointBlobs
from sandwich.core.models.langgraph import Checkpoints
from sandwich.core.models.langgraph import CheckpointWrites
from sandwich.core.types import JsonObject

if TYPE_CHECKING:
    from langchain_core.runnables import RunnableConfig
    from langgraph.types import StateSnapshot

    from sandwich.core.service.agent_service.agent import AgentParameters


@contextmanager
def checkpointer_context(
    existing_checkpointer: BaseCheckpointSaver | None = None,
) -> Generator[BaseCheckpointSaver, Any, None]:
    """A context manager that creates a new PostgresSaver checkpointer (or is no-op for existing)"""
    if existing_checkpointer:
        yield existing_checkpointer
    else:
        with PostgresSaver.from_conn_string(settings.DATABASE_URL) as new_checkpointer:
            yield new_checkpointer


@contextmanager
def store_context(
    existing_store: BaseStore | None = None,
) -> Generator[BaseStore, Any, None]:
    if existing_store:
        yield existing_store
    else:
        with PostgresStore.from_conn_string(settings.DATABASE_URL) as new_store:
            yield new_store


def get_state(
    config: "RunnableConfig",
    **params: "Unpack[AgentParameters]",
) -> "StateSnapshot":
    from sandwich.core.service.agent_service.agent import thrive_agent  # noqa: PLC0415

    with thrive_agent(name="load_snapshot", **params) as agent:
        return agent.get_state(config=config)


def set_state(
    config: "RunnableConfig",
    values: dict[str, Any] | Any | None,
    **params: "Unpack[AgentParameters]",
) -> "StateSnapshot":
    # https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.update_state
    from sandwich.core.service.agent_service.agent import thrive_agent  # noqa: PLC0415

    with thrive_agent(name="set_state", **params) as agent:
        new_config = agent.update_state(config=config, values=values)
        return agent.get_state(config=new_config)


def purge_thread(thread_id: str) -> None:
    """Hard delete stored checkpoints for a given thread id"""
    Checkpoints.objects.filter(thread_id=thread_id).delete()
    CheckpointWrites.objects.filter(thread_id=thread_id).delete()
    CheckpointBlobs.objects.filter(thread_id=thread_id).delete()


def build_assistant_messages(response_format: str, args: JsonObject) -> list[AIMessage | ToolMessage]:
    """Builds an assistant message with a tool use and tool response for the format tool."""
    tool_call_id = f"tooluse_{uuid.uuid4()}"
    return [
        AIMessage(
            content=[
                {
                    "type": "tool_use",
                    "name": response_format,
                    "input": args,
                    "id": tool_call_id,
                }
            ],
            additional_kwargs={},
            response_metadata={
                "ResponseMetadata": {
                    "HTTPHeaders": {
                        "date": format_datetime(timezone.now()),
                    },
                },
                "stopReason": "tool_use",
            },
            tool_calls=[
                {
                    "name": response_format,
                    "args": args,
                    "id": tool_call_id,
                    "type": "tool_call",
                }
            ],
        ),
        ToolMessage(
            content="Returning structured response: .... ",
            name=response_format,
            id=str(uuid.uuid4()),
            tool_call_id=tool_call_id,
        ),
    ]
