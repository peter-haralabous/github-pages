import uuid

import pytest
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import StateSnapshot

from sandwich.core.models.langgraph import Checkpoints
from sandwich.core.service.agent_service.config import configure
from sandwich.core.service.agent_service.memory import get_state


@pytest.fixture
def conversation_thread_id(agent: CompiledStateGraph) -> str:
    thread_id = "test-" + uuid.uuid4().hex
    agent.invoke({"messages": [{"role": "user", "content": "Hello"}]}, config=configure(thread_id))
    return thread_id


@pytest.mark.vcr
def test_load_snapshot(conversation_thread_id: str) -> None:
    snapshot = get_state(config=configure(conversation_thread_id))

    assert isinstance(snapshot, StateSnapshot)
    assert snapshot.config["configurable"]["thread_id"] == conversation_thread_id
    assert snapshot.config["configurable"]["checkpoint_id"] is not None
    assert len(snapshot.values["messages"]) == 2  # user + assistant

    assert Checkpoints.objects.get(checkpoint_id=snapshot.config["configurable"]["checkpoint_id"]) is not None
