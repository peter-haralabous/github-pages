"""Template tags for AI-powered content generation."""

import logging

from django import template
from django.template.base import Node
from django.template.base import Parser
from django.template.base import Token
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from sandwich.core.service.markdown_service import markdown_to_html

logger = logging.getLogger(__name__)

register = template.Library()


class AiBlockNode(Node):
    """
    Template node for {% ai %} blocks.
    """

    def __init__(self, nodelist: template.NodeList, title: str) -> None:
        """
        Initialize the AI block node.

        Args:
            nodelist: List of child nodes inside the {% ai %} block
            title: Title/identifier for this AI block
        """
        self.nodelist = nodelist
        self.title = title

    def render(self, context: template.Context) -> str:
        """
        Render the AI block from pre-generated response, wrapped in a styled container
        """
        ai_responses = context.get("_ai_responses") or {}
        ai_response_obj = ai_responses.get(self.title)
        html_content = (
            markdown_to_html(ai_response_obj.markdown_content, preset="commonmark")
            if ai_response_obj
            else mark_safe("")
        )
        timestamp = ai_response_obj.timestamp if ai_response_obj else None

        logger.debug(
            "Rendering AI response from context",
            extra={"title": self.title, "response_length": len(html_content), "has_timestamp": timestamp is not None},
        )

        return render_to_string(
            "component/ai_block.html",
            {
                "ai_content": html_content,
            },
        )


@register.tag(name="ai")
def do_ai(parser: Parser, token: Token) -> AiBlockNode:
    """
    Template tag for AI-generated content blocks.

    Usage:
        {% ai "Block Title" %}
            Prompt content here, can include {{ variables }} and {% tags %}
        {% endai %}
    """
    try:
        _tag_name, title_arg = token.split_contents()
    except ValueError as e:
        raise template.TemplateSyntaxError(
            f"{token.contents.split()[0]} tag requires exactly one argument: the block title"
        ) from e

    title = title_arg.strip("\"'")
    if title == title_arg:
        raise template.TemplateSyntaxError(f"{token.contents.split()[0]} tag title argument must be a quoted string")

    if not title:
        raise template.TemplateSyntaxError(f"{token.contents.split()[0]} tag title cannot be empty")

    # Parse until {% endai %}
    nodelist = parser.parse(("endai",))
    parser.delete_first_token()

    return AiBlockNode(nodelist, title)
