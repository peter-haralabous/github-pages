"""
Service for rendering templates with AI-generated content using single-pass rendering with preprocessing.

This module provides the AiTemplate class which enables Django templates to include
AI-generated content sections using {% ai %} template tags. The rendering process
uses a single-pass approach with preprocessing:

1. AST Traversal: Read-only traversal to find all {% ai %} blocks in the template
2. Batch Generation: Sends all requests to LLM in a single call for efficiency
3. Single Render: Renders template once with AI-generated responses injected into context

Example Template Usage:
    # Clinical Summary for {{ patient.first_name }} {{ patient.last_name }}

    {% ai "Clinical Assessment" %}
    Based on the following patient data, provide a clinical assessment:
    - Chief Complaint: {{ submission.data.chief_complaint }}
    - Pain Scale: {{ submission.data.pain_scale }}/10
    {% endai %}

    {% ai "Treatment Plan" %}
    Recommend treatment based on the assessment above.
    {% endai %}
"""

import logging
from dataclasses import dataclass

from django.template import Context
from django.template import Template
from django.utils.safestring import SafeString

from sandwich.core.service.ai_summary_service import batch_generate_summaries
from sandwich.core.service.markdown_service import markdown_to_html
from sandwich.core.templatetags.ai_tags import AiBlockNode

logger = logging.getLogger(__name__)


@dataclass
class AiRequest:
    """Represents a request for AI-generated content."""

    title: str
    prompt: str


class AiTemplate(Template):
    """
    Template renderer that uses single-pass rendering with preprocessing for AI content.
    """

    def __init__(self, template_text: str) -> None:
        # Prepend {% load ai_tags %} to ensure the tag is available
        if "{% load ai_tags %}" not in template_text:
            template_with_load = "{% load ai_tags %}\n" + template_text
        else:
            template_with_load = template_text

        super().__init__(template_with_load)

    def find_ai_blocks(self, context: Context) -> list[AiRequest]:
        """
        Find all {% ai %} blocks in a template's AST via recursive traversal.
        """
        ai_requests: list[AiRequest] = []

        # Use Django's built-in recursive traversal
        ai_nodes = self.nodelist.get_nodes_by_type(AiBlockNode)

        for node in ai_nodes:
            assert isinstance(node, AiBlockNode)
            # Extract the prompt by rendering the node's children with context
            prompt = node.nodelist.render(context)
            ai_requests.append(AiRequest(title=node.title, prompt=prompt.strip()))

            logger.debug(
                "Found AI block during AST traversal",
                extra={"title": node.title, "prompt_length": len(prompt)},
            )

        logger.info(
            "AST traversal complete: found AI blocks",
            extra={"request_count": len(ai_requests)},
        )

        return ai_requests

    def render(self, context: dict | Context) -> SafeString:
        """
        Render the template with AI-generated content using single-pass rendering with AST tag preprocessing using AST.
        """
        context_obj = Context(context) if not isinstance(context, Context) else context

        if context_obj.template is None:
            context_obj.template = self

        ai_requests = self.find_ai_blocks(context_obj)
        ai_responses = batch_generate_summaries(ai_requests)

        context_obj.update(
            {
                "_ai_responses": ai_responses,
            }
        )

        rendered_markdown = super().render(context_obj)

        rendered_html = markdown_to_html(rendered_markdown, preset="commonmark")

        logger.info(
            "Template rendered with AI content",
            extra={"request_count": len(ai_requests), "response_count": len(ai_responses)},
        )

        return rendered_html
