from collections.abc import Generator
from typing import Any

import pytest
from django.db import connection
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.store.postgres import PostgresStore
from pytest_django import DjangoDbBlocker

from sandwich.core.service.agent_service.agent import thrive_agent


@pytest.fixture(scope="session")
def agent_memory(django_db_blocker: DjangoDbBlocker) -> Generator[None]:
    """Set up and tear down the Postgres tables for agent memory testing."""
    from django.conf import settings  # noqa: PLC0415

    with (
        django_db_blocker.unblock(),
        PostgresSaver.from_conn_string(settings.DATABASE_URL) as checkpointer,
        PostgresStore.from_conn_string(settings.DATABASE_URL) as store,
    ):
        try:
            checkpointer.setup()
            store.setup()
        except Exception:  # Tables may already exist  # noqa: S110, BLE001
            pass
    yield

    with django_db_blocker.unblock(), connection.cursor() as cursor:
        cursor.execute("""
               DROP TABLE
                checkpoint_blobs,
                checkpoint_migrations,
                checkpoint_writes,
                checkpoints,
                store,
                store_migrations;
               """)


@pytest.fixture
def agent(db: None, agent_memory: None) -> Generator[CompiledStateGraph, Any, None]:
    with thrive_agent("thread_test") as agent:
        yield agent
