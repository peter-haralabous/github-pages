import pytest
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import StateSnapshot

from sandwich.core.models.langgraph import Checkpoints
from sandwich.core.service.agent_service.config import configure
from sandwich.core.service.agent_service.memory import load_snapshot


@pytest.fixture
def conversation_thread_id(agent: CompiledStateGraph) -> str:
    thread_id = "test-thread"
    agent.invoke({"messages": [{"role": "user", "content": "Hello"}]}, config=configure(thread_id))
    return thread_id


@pytest.mark.vcr
def test_load_snapshot(conversation_thread_id: str) -> None:
    snapshot = load_snapshot(config=configure(conversation_thread_id))

    assert isinstance(snapshot, StateSnapshot)
    assert snapshot.config["configurable"]["thread_id"] == conversation_thread_id
    assert snapshot.config["configurable"]["checkpoint_id"] is not None
    assert len(snapshot.values["messages"]) == 2  # user + assistant

    assert Checkpoints.objects.get(checkpoint_id=snapshot.config["configurable"]["checkpoint_id"]) is not None  # type: ignore[attr-defined]
