from typing import Annotated

type HtmlStr = Annotated[str, "HTML formatted string"]
type RePattern = Annotated[str, "A non-compiled regex pattern"]
type UrlNamespace = Annotated[str, "A namespace for urls"]
type UrlName = Annotated[str, "A name for a url"]
type ViewName = Annotated[str, "[<UrlNamespace>:]<UrlName>"]
