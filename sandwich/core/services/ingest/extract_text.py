import json

import pydantic

from sandwich.core.service.llm import ModelName
from sandwich.core.service.llm import get_llm
from sandwich.core.services.ingest.db import save_triples
from sandwich.core.services.ingest.prompt import get_ingest_prompt
from sandwich.core.services.ingest.types import Triple


def extract_facts_from_text(
    text: str,
    llm_name: ModelName = ModelName.CLAUDE_3_SONNET,
    temperature: float | None = None,
    patient=None,
    source_type=None,
) -> list[Triple]:
    """
    Extract facts from unstructured text using an LLM, validate output as Triples, and persist to DB.
    Args:
        text: The unstructured input text.
        llm_name: The LLM model to use.
        temperature: Optional temperature for the LLM.
    Returns:
        List of validated triples.
    """
    llm_client = get_llm(llm_name, temperature=temperature)
    prompt = get_ingest_prompt(text)
    raw_output = llm_client.invoke(prompt)
    output_text = getattr(raw_output, "content", raw_output)
    if not isinstance(output_text, str):
        output_text = str(output_text)
    try:
        triples_data = json.loads(output_text)
        triples = [Triple.model_validate(triple) for triple in triples_data]

        save_triples(triples, patient=patient, source_type=source_type)
    except (json.JSONDecodeError, pydantic.ValidationError, TypeError) as e:
        msg = f"Failed to parse or validate LLM output: {e}\nRaw output: {output_text}"
        raise ValueError(msg) from e
    else:
        return triples
