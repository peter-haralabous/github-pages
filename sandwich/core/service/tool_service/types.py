from typing import TypedDict

from sandwich.core.types import JsonValue
from sandwich.core.types import ModelLabel
from sandwich.core.types import UuidStr


class ModelDict(TypedDict):
    model: ModelLabel
    pk: UuidStr
    fields: dict[str, JsonValue]
