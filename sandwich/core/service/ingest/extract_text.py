from typing import cast

from django.utils import timezone
from langchain_core.language_models import BaseChatModel

from sandwich.core.models import Document
from sandwich.core.models import Patient
from sandwich.core.models import Provenance
from sandwich.core.models.provenance import SourceType
from sandwich.core.service.ingest.db import save_triples
from sandwich.core.service.ingest.extract_pdf import _process_response
from sandwich.core.service.ingest.prompt import get_ingest_prompt
from sandwich.core.service.ingest.response_models import IngestPromptWithContextResponse
from sandwich.core.service.ingest.types import Triple


def extract_facts_from_text(
    text: str,
    llm_client: BaseChatModel,
    document: Document | None = None,
    patient: Patient | None = None,
) -> list[Triple]:
    """
    Extract facts from unstructured text using an LLM, validate output as Triples, and persist to DB.
    """
    structured_llm_client = llm_client.with_structured_output(
        schema=IngestPromptWithContextResponse, method="json_mode"
    )

    prompt = get_ingest_prompt(text)
    response = cast("IngestPromptWithContextResponse", structured_llm_client.invoke(prompt))
    assert isinstance(response, IngestPromptWithContextResponse), (
        f"expected an IngestPromptWithContextResponse, but got {type(response)}"
    )
    triples = _process_response(response, patient, 0)
    if triples:
        provenance = Provenance.objects.create(
            document=document,
            source_type=SourceType.DOCUMENT if document else SourceType.UNKNOWN,
            extracted_at=timezone.now(),
            extracted_by=llm_client.__class__.__name__,
        )
        save_triples(triples, provenance, patient=patient)
    return triples
