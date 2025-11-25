"""Template tags for AI-powered content generation."""

import logging

from django import template
from django.template.base import Node
from django.template.base import Parser
from django.template.base import Token

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
        Render the AI block by fetching the pre-generated response from the preprocessor.
        """
        ai_responses_dict = context.get("_ai_responses")
        response = ""
        if ai_responses_dict is not None:
            response = ai_responses_dict.get(self.title, "")

        logger.debug(
            "Rendering AI response from context",
            extra={"title": self.title, "response_length": len(response)},
        )

        return response


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

    # Remove quotes from title
    if title_arg[0] == title_arg[-1] and title_arg[0] in ('"', "'"):
        title = title_arg[1:-1]
    else:
        raise template.TemplateSyntaxError(f"{token.contents.split()[0]} tag title argument must be a quoted string")

    if not title:
        raise template.TemplateSyntaxError(f"{token.contents.split()[0]} tag title cannot be empty")

    # Parse until {% endai %}
    nodelist = parser.parse(("endai",))
    parser.delete_first_token()

    return AiBlockNode(nodelist, title)
