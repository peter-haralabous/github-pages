import json

import pydantic
from django.utils import timezone
from langchain_core.language_models import BaseChatModel

from sandwich.core.models import Document
from sandwich.core.models import Patient
from sandwich.core.models import Provenance
from sandwich.core.service.ingest.db import save_triples
from sandwich.core.service.ingest.prompt import get_ingest_prompt
from sandwich.core.service.ingest.types import Triple


def extract_facts_from_text(
    text: str,
    llm_client: BaseChatModel,
    document: Document | None = None,
    patient: Patient | None = None,
    # FIXME: source_type should not be optional;
    #        `text` seems more appropriate but requires a `User` on the provenance record
    source_type: str = "unknown",
) -> list[Triple]:
    """
    Extract facts from unstructured text using an LLM, validate output as Triples, and persist to DB.
    """
    prompt = get_ingest_prompt(text)
    raw_output = llm_client.invoke(prompt)
    output_text = getattr(raw_output, "content", raw_output)
    if not isinstance(output_text, str):
        output_text = str(output_text)
    try:
        triples_data = json.loads(output_text)
        triples = [Triple.model_validate(triple) for triple in triples_data]

        if triples:
            provenance = Provenance.objects.create(
                document=document,
                source_type=source_type,
                extracted_at=timezone.now(),
                extracted_by=llm_client.__class__.__name__,
            )
            save_triples(triples, provenance, patient=patient)
    except (json.JSONDecodeError, pydantic.ValidationError, TypeError) as e:
        msg = f"Failed to parse or validate LLM output: {e}\nRaw output: {output_text}"
        raise ValueError(msg) from e
    else:
        return triples
