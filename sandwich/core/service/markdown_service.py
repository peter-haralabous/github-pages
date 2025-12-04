from collections.abc import Mapping
from typing import Any
from typing import Literal

from django.utils.safestring import SafeString
from django.utils.safestring import mark_safe
from markdown_it import MarkdownIt


def markdown_to_html(
    markdown_text: str,
    preset: Literal["zero", "commonmark", "js-default"] = "js-default",
    options: Mapping[str, Any] | None = None,
) -> SafeString:
    """Convert Markdown text to HTML using markdown-it-py.

    This is configured by default to use the "js-default" preset, which is a minimal configuration
    without any additional plugins or features enabled (raw html in the markdown is disabled).

    Using the "commonmark" preset enables a more feature-rich configuration that adheres to the
    CommonMark specification and is not safe against untrusted input (raw html is enabled).

    See:
    - https://markdown-it-py.readthedocs.io/en/latest/security.html
    - https://markdown-it-py.readthedocs.io/en/latest/using.html#the-parser

    """

    parser = MarkdownIt(config=preset, options_update=options)
    return mark_safe(parser.render(markdown_text))  # noqa: S308
