import datetime
from collections.abc import Generator
from collections.abc import Iterable
from email.utils import parsedate_to_datetime
from functools import cached_property
from typing import TYPE_CHECKING
from typing import Any

from django.template.context import ContextDict
from django.template.loader import render_to_string
from django.utils.safestring import SafeString
from langchain_core.messages import AIMessage
from langchain_core.messages import BaseMessage
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from sandwich.core.models import Patient
from sandwich.core.service.agent_service.config import configure
from sandwich.core.service.agent_service.memory import build_assistant_messages
from sandwich.core.service.agent_service.memory import get_state
from sandwich.core.service.agent_service.memory import set_state
from sandwich.core.service.markdown_service import markdown_to_html
from sandwich.core.service.prompt_service.template import template_contents
from sandwich.users.models import User

if TYPE_CHECKING:
    from langchain_core.runnables import RunnableConfig
    from langgraph.types import StateSnapshot

    from sandwich.core.service.chat_service.response import Button


def _timestamp_from_message(message: BaseMessage) -> datetime.datetime | None:
    if isinstance(message, HumanMessage):
        raw_timestamp = message.response_metadata.get("timestamp")
        if raw_timestamp:
            if isinstance(raw_timestamp, datetime.datetime):
                return raw_timestamp
            return datetime.datetime.fromisoformat(raw_timestamp)
    elif isinstance(message, AIMessage):
        raw_timestamp = message.response_metadata.get("ResponseMetadata", {}).get("HTTPHeaders", {}).get("date")
        if raw_timestamp:
            return parsedate_to_datetime(raw_timestamp)
    return None


def initial_chat_messages(config: "RunnableConfig", patient: Patient) -> list[SafeString]:
    messages = build_assistant_messages(
        "ChatResponse",
        {
            "message": template_contents("chat_initial.md").format(patient_name=patient.full_name),
            "buttons": [],
        },
    )
    state = set_state(config, values={"messages": messages})
    return list(html_message_list(state.values.get("messages", []), patient=patient))


def load_chat_messages(config: "RunnableConfig", patient: Patient) -> list[SafeString]:
    state: StateSnapshot = get_state(config)
    if existing_messages := state.values.get("messages"):
        return list(html_message_list(existing_messages, patient=patient))
    return initial_chat_messages(config, patient=patient)


def html_message_list(messages: Iterable[BaseMessage], patient: Patient) -> Generator[SafeString, Any, None]:
    for message in messages:
        timestamp = _timestamp_from_message(message)
        if isinstance(message, HumanMessage):
            yield user_message(patient, str(message.content), timestamp)

        elif isinstance(message, AIMessage):
            for tool_call in message.tool_calls:
                if tool_call["name"] == "ChatResponse":
                    yield assistant_message(
                        content=tool_call["args"]["message"],
                        buttons=tool_call["args"]["buttons"],
                        timestamp=timestamp,
                    )


def user_message(
    patient: Patient,
    content: str,
    timestamp: datetime.datetime | None,
    context: ContextDict | dict[str, Any] | None = None,
) -> SafeString:
    if context is None:
        context = {}
    context.update({"patient": patient, "message": content, "timestamp": timestamp})
    return render_to_string("patient/chatty/partials/user_message.html", context)


def assistant_message(
    content: str,
    buttons: "list[Button]",
    timestamp: datetime.datetime | None,
    context: ContextDict | dict[str, Any] | None = None,
) -> SafeString:
    if context is None:
        context = {}
    context.update({"message": markdown_to_html(content), "buttons": buttons, "timestamp": timestamp})
    return render_to_string("patient/chatty/partials/assistant_message.html", context)


class ChatContext(BaseModel):
    patient_id: str

    @cached_property
    def patient(self) -> Patient:
        return Patient.objects.get(id=self.patient_id)

    @cached_property
    def thread_id(self) -> str:
        return f"{self.user_id}-{self.patient_id}"

    @cached_property
    def user(self) -> User:
        user = self.patient.user
        if user is None:
            raise ValueError(f"Patient {self.patient_id} has no associated user.")
        return user

    @cached_property
    def user_id(self) -> str:
        return str(self.user.id)

    def config(self, config: "RunnableConfig | None" = None) -> "RunnableConfig":
        return configure(self.thread_id, config)
