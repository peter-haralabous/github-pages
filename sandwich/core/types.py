from typing import Annotated

EMPTY_VALUE_DISPLAY = "—"

type HtmlStr = Annotated[str, "HTML formatted string"]
type RePattern = Annotated[str, "A non-compiled regex pattern"]
type UrlNamespace = Annotated[str, "A namespace for urls"]
type UrlName = Annotated[str, "A name for a url"]
type ViewName = Annotated[str, "[<UrlNamespace>:]<UrlName>"]

# Json; see https://www.json.org/json-en.html
type JsonPrimitive = str | int | float | bool | None
type JsonArray = list["JsonValue"]
type JsonObject = dict[str, "JsonValue"]
type JsonValue = JsonObject | JsonArray | JsonPrimitive

type ShallowJsonObject = JsonPrimitive | dict[str, JsonPrimitive] | list[JsonPrimitive]
