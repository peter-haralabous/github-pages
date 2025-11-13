import datetime
from email.utils import parsedate_to_datetime
from typing import TYPE_CHECKING
from typing import Unpack

from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.safestring import SafeString
from langchain_core.messages import AIMessage
from langchain_core.messages import HumanMessage

from sandwich.core.models import Patient
from sandwich.core.service.agent_service.memory import load_snapshot
from sandwich.core.service.chat_service.agents import chat_agent
from sandwich.core.service.markdown_service import markdown_to_html
from sandwich.users.models import User

if TYPE_CHECKING:
    from langchain.agents import AgentState
    from langchain_core.runnables import RunnableConfig
    from langgraph.types import StateSnapshot

    from sandwich.core.service.agent_service.agent import AgentParameters
    from sandwich.core.service.chat_service.response import Button
    from sandwich.core.service.chat_service.response import ChatResponse


def receive_chat_message(
    message_id: str,
    message: str,
    config: "RunnableConfig",
    user: User | None = None,
    patient: Patient | None = None,
    **params: "Unpack[AgentParameters]",
) -> "ChatResponse":
    state: AgentState = {
        "messages": [
            HumanMessage(
                content=message,
                response_metadata={
                    "timestamp": timezone.now().isoformat(),
                    "message_id": message_id,
                },
            ),
        ],
    }
    with chat_agent(user, patient, **params) as agent:
        return agent.invoke(
            input=state,
            config=config,
        )["structured_response"]


def load_chat_messages(config: "RunnableConfig") -> list[SafeString]:
    state: StateSnapshot = load_snapshot(config)
    messages: list[SafeString] = []

    for message in state.values.get("messages", []):
        if isinstance(message, HumanMessage):
            raw_timestamp = message.response_metadata["timestamp"]
            messages.append(
                user_message(
                    message.content,  # type: ignore[arg-type]
                    datetime.datetime.fromisoformat(raw_timestamp),
                )
            )
        elif isinstance(message, AIMessage):
            for tool_call in message.tool_calls:
                if tool_call["name"] == "ChatResponse":
                    raw_timestamp = message.response_metadata["ResponseMetadata"]["HTTPHeaders"]["date"]
                    messages.append(
                        assistant_message(
                            content=tool_call["args"]["message"],
                            buttons=tool_call["args"]["buttons"],
                            timestamp=parsedate_to_datetime(raw_timestamp),
                        )
                    )

    return messages


def user_message(content: str, timestamp: datetime.datetime) -> SafeString:
    context = {"message": content, "timestamp": timestamp}
    return render_to_string("patient/chatty/partials/user_message.html", context)


def assistant_message(content: str, buttons: "list[Button]", timestamp: datetime.datetime) -> SafeString:
    context = {"message": markdown_to_html(content), "buttons": buttons, "timestamp": timestamp}
    return render_to_string("patient/chatty/partials/assistant_message.html", context)
