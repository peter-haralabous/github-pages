from collections.abc import Generator
from contextlib import contextmanager
from typing import TYPE_CHECKING
from typing import Any
from typing import Unpack

from django.conf import settings
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.base import BaseStore
from langgraph.store.postgres import PostgresStore

from sandwich.core.models.langgraph import CheckpointBlobs
from sandwich.core.models.langgraph import Checkpoints
from sandwich.core.models.langgraph import CheckpointWrites

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


def load_snapshot(
    config: "RunnableConfig",
    **params: "Unpack[AgentParameters]",
) -> "StateSnapshot":
    from sandwich.core.service.agent_service.agent import thrive_agent  # noqa: PLC0415

    with thrive_agent(name="load_snapshot", **params) as agent:
        return agent.get_state(config=config)


def purge_thread(thread_id: str) -> None:
    """Hard delete stored checkpoints for a given thread id"""
    Checkpoints.objects.filter(thread_id=thread_id).delete()  # type: ignore[attr-defined]
    CheckpointWrites.objects.filter(thread_id=thread_id).delete()  # type: ignore[attr-defined]
    CheckpointBlobs.objects.filter(thread_id=thread_id).delete()  # type: ignore[attr-defined]
