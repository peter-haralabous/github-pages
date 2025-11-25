import logging
from collections.abc import Callable

import django
from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.types import Command

logger = logging.getLogger(__name__)


@wrap_tool_call
def close_db_connections(
    request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    response = handler(request)
    # Ensure database connections are closed after the tool call
    django.db.close_old_connections()  # type: ignore[attr-defined]
    return response


@wrap_tool_call
def exception_handling(
    request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    try:
        response = handler(request)
    except Exception as exc_info:
        logger.exception(
            "Tool call exception",
            exc_info=exc_info,
            extra={
                "tool_call": {
                    "name": request.tool_call.get("name"),
                    "id": request.tool_call.get("id"),
                }
            },
        )
        return ToolMessage(content=f"An error occurred: {exc_info!s}")
    return response
