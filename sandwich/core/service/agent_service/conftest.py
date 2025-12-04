from collections.abc import Generator
from typing import Any

import pytest
from langgraph.graph.state import CompiledStateGraph

from sandwich.core.service.agent_service.agent import thrive_agent


@pytest.fixture
def agent(db: None) -> Generator[CompiledStateGraph, Any, None]:
    with thrive_agent("thread_test") as agent:
        yield agent
