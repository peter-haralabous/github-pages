import argparse
import inspect
import json
from typing import Any
from typing import cast

# https://www.json.org/json-en.html
type JsonPrimitive = str | int | float | bool | None
type JsonArray = list["JsonValue"]
type JsonObject = dict[str, "JsonValue"]
type JsonValue = JsonObject | JsonArray | JsonPrimitive

type ShallowJsonObject = JsonPrimitive | dict[str, JsonPrimitive] | list[JsonPrimitive]


jsonable_types = [str, int, float, bool, bytes, type(None), list, tuple, dict, set]


def jsonable_object(obj: Any) -> JsonObject:
    """Take an arbitrary object and return a json-serializable dictionary of attributes"""
    names = [
        name for name, member in inspect.getmembers(obj) if not name.startswith("_") and type(member) in jsonable_types
    ]
    object_string = json.dumps({name: getattr(obj, name) for name in names}, default=str)
    return json.loads(object_string)


def json_object_type(value: str) -> JsonObject:
    try:
        data = json.loads(value)
    except json.JSONDecodeError as exc_info:
        msg = f"{value} is not a valid JSON"
        raise argparse.ArgumentTypeError(msg) from exc_info

    if not isinstance(data, dict):
        msg = f"{value} is not a valid JSON Object"
        raise argparse.ArgumentTypeError(msg)
    return cast("JsonObject", data)


def json_array_type(value: str) -> JsonArray:
    try:
        data = json.loads(value)
    except json.JSONDecodeError as exc_info:
        msg = f"{value} is not a valid JSON"
        raise argparse.ArgumentTypeError(msg) from exc_info

    if not isinstance(data, list):
        msg = f"{value} is not a valid JSON Array"
        raise argparse.ArgumentTypeError(msg)
    return cast("JsonArray", data)
