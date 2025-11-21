from typing import Annotated

EMPTY_VALUE_DISPLAY = "—"
DATE_DISPLAY_FORMAT = "%Y-%m-%d"  # For python date formatting
DJANGO_DATE_FORMAT = "Y-m-d"  # Django date filter format for ISO consistent with DATE_DISPLAY_FORMAT
DJANGO_DATE_TIME_FORMAT = "Y-m-d H:i"

type HtmlStr = Annotated[str, "HTML formatted string"]
type RePattern = Annotated[str, "A non-compiled regex pattern"]
type UrlNamespace = Annotated[str, "A namespace for urls"]
type UrlName = Annotated[str, "A name for a url"]
type UuidStr = Annotated[str, "A string representation of a UUID"]
type ViewName = Annotated[str, "[<UrlNamespace>:]<UrlName>"]

type ModelLabel = Annotated[str, "Django model label in the form 'app_label.model_name'"]

# Json; see https://www.json.org/json-en.html
type JsonPrimitive = str | int | float | bool | None
type JsonArray = list["JsonValue"]
type JsonObject = dict[str, "JsonValue"]
type JsonValue = JsonObject | JsonArray | JsonPrimitive

type ShallowJsonObject = JsonPrimitive | dict[str, JsonPrimitive] | list[JsonPrimitive]
