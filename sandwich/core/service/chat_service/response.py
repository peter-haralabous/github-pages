from typing import Literal
from typing import TypedDict

from langchain_core.messages import BaseMessage
from pydantic import BaseModel
from pydantic import Field


class Button(BaseModel):
    """A button will be rendered in the chat interface as a clickable option for the user to select"""

    label: str = Field(description="The text displayed on the button")
    action: Literal["prompt"] = Field(
        description="""
    The type of action for the button to take:
      - "prompt": When clicked, the button will load the associated value as a user message in the chat.
    """
    )
    value: str = Field(description="The value to be used on the action")


class ChatResponse(BaseModel):
    message: str
    buttons: list[Button]


class ChatResponseMessage(TypedDict):
    """See BaseChatModel.with_structured_output(include_raw=True)"""

    raw: BaseMessage
    parsed: ChatResponse | None
    parsing_error: str | None
