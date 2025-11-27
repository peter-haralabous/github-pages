import abc
import dataclasses
import datetime
import uuid
from enum import StrEnum
from typing import TYPE_CHECKING
from typing import Unpack

from django.template import loader
from django.utils import timezone
from django.utils.safestring import SafeString
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from sandwich.core.service.chat_service.agents import ChatAgentContext
from sandwich.core.service.chat_service.agents import chat_agent
from sandwich.core.service.chat_service.chat import ChatContext
from sandwich.core.service.chat_service.response import ChatResponse
from sandwich.core.service.chat_service.sse import send_assistant_message
from sandwich.core.service.chat_service.sse import send_assistant_thinking
from sandwich.core.service.chat_service.sse import send_feed_item
from sandwich.core.service.ingest.extract_records import RecordsResponse
from sandwich.core.service.prompt_service.chat import file_processed_context
from sandwich.core.service.prompt_service.chat import file_processed_template

if TYPE_CHECKING:
    from langgraph._internal._typing import StateLike

    from sandwich.core.service.agent_service.agent import AgentParameters


class AssistantResponseMixin(abc.ABC):
    """Mixin for chat events that require an assistant response."""

    needs_assistant_response = True

    @abc.abstractmethod
    def input_for_assistant_response(self) -> "StateLike": ...


class UpdatesFeedMixin(abc.ABC):
    """Mixin for chat events that should update the chat feed."""

    updates_feed = True

    @abc.abstractmethod
    def feed_item_html(self) -> SafeString: ...


class ChatEventType(StrEnum):
    ASSISTANT_MESSAGE = "assistant_message"
    USER_MESSAGE = "user_message"
    FILE_UPLOADED = "file_uploaded"
    FILE_PROCESSING = "file_processing"
    FILE_PROCESSED = "file_processed"


class ChatEvent(BaseModel, abc.ABC):
    context: ChatContext
    type: ChatEventType

    id: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime.datetime = dataclasses.field(default_factory=lambda: timezone.now())


class AssistantMessageEvent(ChatEvent):
    type: ChatEventType = ChatEventType.ASSISTANT_MESSAGE
    response: ChatResponse


class IncomingChatEvent(ChatEvent, abc.ABC):
    needs_assistant_response: bool = False
    updates_feed: bool = False

    def input_for_assistant_response(self) -> "StateLike":
        raise NotImplementedError("This event does not support assistant responses.")

    def feed_item_html(self) -> SafeString:
        raise NotImplementedError("This event does not support feed items")


class FileUploadedEvent(UpdatesFeedMixin, IncomingChatEvent):
    type: ChatEventType = ChatEventType.FILE_UPLOADED
    document_id: str
    document_filename: str

    def feed_item_html(self) -> SafeString:
        return loader.render_to_string(
            "patient/chatty/partials/feed_item.html",
            context={
                "document_id": self.document_id,
                "item_background_class": "bg-gray-200",
                "item_icon_name": "clock",
                "item_icon_class": "stroke-gray-800",
                "item_name": self.document_filename,
                "item_status": "Queued",
            },
        )


class FileProcessingEvent(UpdatesFeedMixin, IncomingChatEvent):
    type: ChatEventType = ChatEventType.FILE_PROCESSING
    document_id: str
    document_filename: str

    def feed_item_html(self) -> SafeString:
        return loader.render_to_string(
            "patient/chatty/partials/feed_item.html",
            context={
                "document_id": self.document_id,
                "item_background_class": "bg-blue-100",
                "item_icon_name": "loader-circle",
                "item_icon_class": "animate-spin stroke-blue-800",
                "item_name": self.document_filename,
                "item_status": "Processing",
            },
        )


class FileProcessedEvent(AssistantResponseMixin, UpdatesFeedMixin, IncomingChatEvent):
    type: ChatEventType = ChatEventType.FILE_PROCESSED
    document_id: str
    document_filename: str
    records: RecordsResponse

    def feed_item_html(self) -> SafeString:
        return loader.render_to_string(
            "patient/chatty/partials/feed_item.html",
            context={
                "document_id": self.document_id,
                "item_background_class": "bg-green-100",
                "item_icon_name": "check",
                "item_icon_class": "animate-tada stroke-green-800",
                "item_name": self.document_filename,
                "item_status": "Processed",
            },
        )

    def input_for_assistant_response(self) -> "StateLike":
        return file_processed_template.invoke(file_processed_context(self))


class UserMessageEvent(AssistantResponseMixin, IncomingChatEvent):
    type: ChatEventType = ChatEventType.USER_MESSAGE
    content: str

    def input_for_assistant_response(self) -> "StateLike":
        return {  # type: ignore[return-value]
            "messages": [
                HumanMessage(
                    content=self.content,
                    response_metadata={
                        "timestamp": self.timestamp,
                        "message_id": self.id,
                    },
                ),
            ],
        }


def receive_chat_event(
    event: "IncomingChatEvent",
    **params: "Unpack[AgentParameters]",
) -> None:
    if event.updates_feed:
        send_feed_item(event)

    if event.needs_assistant_response:
        # 1. Notify that the assistant is thinking
        send_assistant_thinking(event)

        # 2. Process the event with the chat agent
        with chat_agent(event.context.user, event.context.patient, **params) as agent:
            response = agent.invoke(
                agent=agent,
                input=event.input_for_assistant_response(),
                config=event.context.config(),
                context=ChatAgentContext(),  # type: ignore[arg-type]
            )

        # 3. Send the assistant's message
        message = AssistantMessageEvent(response=response["structured_response"], context=event.context)
        send_assistant_message(message)
