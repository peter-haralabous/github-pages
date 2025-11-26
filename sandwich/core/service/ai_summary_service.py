"""
Service for generating AI summaries using LLM with structured responses.

This module handles communication with the LLM to generate medical summaries
based on template requests.
"""

import logging
import uuid
from typing import TYPE_CHECKING

from langchain.agents.structured_output import ToolStrategy
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from pydantic import Field

from sandwich.core.service.agent_service.agent import thrive_agent
from sandwich.core.service.agent_service.config import configure

if TYPE_CHECKING:
    from sandwich.core.service.ai_template import AiRequest

logger = logging.getLogger(__name__)


class AISummaryResponse(BaseModel):
    """
    Response from AI containing multiple sections in order.
    """

    sections: list[str] = Field(description="Array of markdown sections. MUST be in the same order as requested.")


def batch_generate_summaries(
    requests: "list[AiRequest]",
) -> dict[str, str]:
    """
    Generate AI summaries for multiple section requests in a single LLM call.
    """
    if not requests:
        logger.info("No AI requests to process")
        return {}

    try:
        logger.info(
            "Starting batch summary generation",
            extra={"request_count": len(requests)},
        )

        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(requests)

        with thrive_agent(
            name="ai_summary_agent",
            system_prompt=system_prompt,
            response_format=ToolStrategy(AISummaryResponse),
        ) as agent:
            thread_id = f"ai_summary_{uuid.uuid4().hex}"
            response = agent.invoke(
                input={"messages": [HumanMessage(content=user_prompt)]},
                config=configure(thread_id),
            )

        structured_response = response["structured_response"]
        if structured_response:
            responses = parse_ai_response(structured_response, requests)
            logger.info(
                "Successfully generated AI summaries",
                extra={
                    "request_count": len(requests),
                    "response_count": len(responses),
                },
            )
            return responses

        logger.warning(
            "AI response parsing failed, using fallback",
            extra={"structured_response": structured_response},
        )
        return _fallback_responses(requests)

    except Exception:
        logger.exception(
            "Error generating AI summaries, using fallback",
            extra={"request_count": len(requests)},
        )
        return _fallback_responses(requests)


def build_system_prompt() -> str:
    """
    Build the system prompt for medical summary generation.

    Returns:
        System prompt string for the AI agent
    """
    return """You are a medical AI assistant specialized in generating concise, accurate clinical summaries.

Your role is to:
- Analyze patient medical information and generate clear, professional summaries
- Organize information into well-structured sections with appropriate headings
- Use medical terminology appropriately while remaining clear
- Focus on clinically relevant information
- Format output as markdown with proper section headers (using ##)
- Be concise but comprehensive

IMPORTANT:
- You MUST return sections in the EXACT ORDER they are requested
- Each section should have a clear heading starting with ##
- Write in a professional medical tone
- Do not include disclaimers or meta-commentary
- Do not make up information - only summarize what is provided
- If information is insufficient, note that briefly
"""


def build_user_prompt(
    requests: "list[AiRequest]",
) -> str:
    """
    Build the user prompt by combining all section requests, emphasizing order.
    """
    prompt_parts = [
        "Generate medical summary sections IN THE EXACT ORDER listed below:",
        "",
    ]

    for i, request in enumerate(requests, 1):
        prompt_parts.extend(
            [
                f"## Section {i}: {request.title}",
                request.prompt.strip(),
                "",
            ]
        )

    prompt_parts.extend(
        [
            "---",
            "",
            "Each section should start with a markdown heading (##).",
        ]
    )

    return "\n".join(prompt_parts)


def parse_ai_response(
    response: AISummaryResponse,
    requests: "list[AiRequest]",
) -> dict[str, str]:
    """
    Parse AI response and match sections to original requests by index position.
    """
    if len(response.sections) != len(requests):
        logger.error(
            "Section count mismatch between requests and responses",
            extra={
                "expected_count": len(requests),
                "received_count": len(response.sections),
                "request_titles": [req.title for req in requests],
            },
        )
        msg = (
            f"Section count mismatch: expected {len(requests)} sections, "
            f"received {len(response.sections)} sections. "
            f"This is critical for medical accuracy."
        )
        raise ValueError(msg)

    matched_responses: dict[str, str] = {}

    for request, content in zip(requests, response.sections, strict=True):
        matched_responses[request.title] = content

    return matched_responses


def _fallback_responses(requests: "list[AiRequest]") -> dict[str, str]:
    """
    Generate fallback responses when AI generation fails.
    """
    return {request.title: f"[Summary for {request.title} is temporarily unavailable]" for request in requests}
