from enum import StrEnum
from typing import Any

from django.conf import settings
from langchain_aws import ChatBedrock
from langchain_aws import ChatBedrockConverse
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI


class ModelName(StrEnum):
    DEFAULT = "claude-sonnet-4-5"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    CLAUDE_SONNET_4_5 = "claude-sonnet-4-5"
    GPT_OSS = "gpt-oss-120b"
    GEMINI = "gemini-2.5-pro"
    GEMINI_FLASH = "gemini-2.5-flash"


def _extract_region(arn: str | None) -> str | None:
    """extract the region from an ARN."""
    if arn and arn.startswith("arn:aws:"):
        return arn.split(":")[3]
    return None


def get_claude_3_sonnet(temperature: float | None = None) -> ChatBedrock:
    """
    OK for PHI handling.

    Claude 3 is kinda crap, but is available with Bedrock on-demand in ca-central-1.
    """
    model_kwargs = {}
    if temperature is not None:
        model_kwargs["temperature"] = temperature

    base_model = "anthropic.claude-3-sonnet-20240229-v1:0"
    return ChatBedrock(
        model=settings.BEDROCK_CLAUDE_3_SONNET_ARN or base_model,
        base_model=base_model,
        provider="anthropic",
        max_tokens=16384,  # it looks like this might be 1024 by default, but I can't find an authoritive source
        model_kwargs=model_kwargs,
    )


def get_claude_sonnet_4_5(temperature: float | None = None) -> ChatBedrockConverse:
    """
    OK for PHI handling.

    NOTE: Claude Sonnet 4.5 uses cross-region inference in ca-central-1, so we don't know where the data is being
    processed. AWS assures us that it never leaves their network, and that data isn't stored.
    """
    base_model = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
    kwargs: dict[str, Any] = {
        "model": settings.BEDROCK_CLAUDE_SONNET_4_5_ARN or base_model,
        "base_model": base_model.removeprefix("global."),
        "provider": "anthropic",
    }
    if region_name := _extract_region(settings.BEDROCK_CLAUDE_SONNET_4_5_ARN):
        kwargs["region_name"] = region_name
    if temperature is not None:
        kwargs["temperature"] = temperature
    return ChatBedrockConverse(**kwargs)


def get_gpt_oss(temperature: float | None = None) -> ChatBedrockConverse:
    """
    OK for PHI handling.

    NOTE: We're not **yet** hosting this in Canada, but we could in the future if needed. As long as we're only doing
    demos and not selling a product to BC healthcare providers, this should be fine.
    """
    base_model = "openai.gpt-oss-120b-1:0"
    kwargs: dict[str, Any] = {
        "model": settings.BEDROCK_GPT_OSS_120B_ARN or base_model,
        "base_model": base_model,
        "provider": "openai",
    }
    if region_name := _extract_region(settings.BEDROCK_GPT_OSS_120B_ARN):
        kwargs["region_name"] = region_name
    else:
        kwargs["region_name"] = "us-west-2"
    if temperature is not None:
        kwargs["temperature"] = temperature
    return ChatBedrockConverse(**kwargs)


def get_gemini(temperature: float | None = None) -> ChatGoogleGenerativeAI:
    """
    _NOT_ for PHI handling, as Gemini models can't be hosted in Canada.
    """
    if not settings.GEMINI_API_KEY:
        msg = "GEMINI_API_KEY is not set in settings."
        raise ValueError(msg)
    kwargs: dict[str, Any] = {
        "model": "gemini-2.5-pro",
        "google_api_key": settings.GEMINI_API_KEY,
    }
    if temperature is not None:
        kwargs["temperature"] = temperature
    return ChatGoogleGenerativeAI(**kwargs)


def get_gemini_flash(temperature: float | None = None) -> ChatGoogleGenerativeAI:
    """
    _NOT_ for PHI handling, as Gemini models can't be hosted in Canada.
    """
    if not settings.GEMINI_API_KEY:
        msg = "GEMINI_API_KEY is not set in settings."
        raise ValueError(msg)
    kwargs: dict[str, Any] = {
        "model": "gemini-2.5-flash",
        "google_api_key": settings.GEMINI_API_KEY,
    }
    if temperature is not None:
        kwargs["temperature"] = temperature
    return ChatGoogleGenerativeAI(**kwargs)


def get_llm(llm_name: ModelName, temperature: float | None = None) -> BaseChatModel:
    match llm_name:
        case ModelName.CLAUDE_3_SONNET:
            return get_claude_3_sonnet(temperature=temperature)
        case ModelName.CLAUDE_SONNET_4_5:
            return get_claude_sonnet_4_5(temperature=temperature)
        case ModelName.GPT_OSS:
            return get_gpt_oss(temperature=temperature)
        case ModelName.GEMINI:
            return get_gemini(temperature=temperature)
        case ModelName.GEMINI_FLASH:
            return get_gemini_flash(temperature=temperature)
        case _:
            msg = f"Unsupported LLM: {llm_name}"
            raise ValueError(msg)
