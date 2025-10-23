import base64
import logging
from datetime import UTC
from datetime import datetime
from io import BytesIO

import pydantic
from langchain_core.language_models import BaseChatModel
from pdf2image import convert_from_path

from sandwich.core.services.ingest.db import save_triples
from sandwich.core.services.ingest.prompt import get_ingest_prompt
from sandwich.core.services.ingest.response_models import IngestPromptWithContextResponse
from sandwich.core.services.ingest.schema import PREDICATE_NAMES

logger = logging.getLogger(__name__)


def convert_pages(pdf_path: str) -> list[bytes]:
    """
    Convert each page of a PDF to PNG image bytes (for LLM image input).
    """
    images = convert_from_path(pdf_path, fmt="png")
    page_pngs = []
    for img in images:
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        page_pngs.append(buf.getvalue())
    return page_pngs


def _build_image_messages(page_index: int, base64_img: str) -> list:
    prompt = get_ingest_prompt(
        input_text="[See attached image of clinical document page]",
        input_description=f"This is page {page_index} of a scanned clinical document.",
    )
    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_img}"}},
            ],
        }
    ]


def _provenance_dict(page_index: int, llm_client) -> dict:
    return {
        "page": page_index,
        "extracted_at": datetime.now(UTC).isoformat() + "Z",
        "extracted_by": llm_client.__class__.__name__,
    }


def _validate_or_trim(parsed):
    try:
        return IngestPromptWithContextResponse.model_validate(parsed)
    except pydantic.ValidationError:
        if isinstance(parsed, dict) and "triples" in parsed and isinstance(parsed["triples"], list):
            parsed["triples"] = parsed["triples"][:-1]
            result = IngestPromptWithContextResponse.model_validate(parsed)
            logger.warning("Skipped invalid last record in triples extraction")
            return result


def _filter_triples(parsed):
    """Filter out invalid triples from a list."""
    filtered = []
    for t in parsed:
        subject = t.get("subject")
        node = subject.get("node") if isinstance(subject, dict) else None
        if not isinstance(node, dict):
            continue
        if t.get("normalized_predicate") is None or t.get("object") is None:
            continue
        filtered.append(t)
    return {"triples": filtered}


def _process_response(response, patient, page_index: int, llm_client) -> list:
    """
    Process LLM response to extract and validate triples, filtering out invalid ones.
    """
    try:
        triples = response.triples
        filtered_triples: list = []
        for t in triples:
            pred = getattr(t, "normalized_predicate", None)
            pred_label = pred.predicate_type if (pred is not None and hasattr(pred, "predicate_type")) else pred
            if pred_label not in set(PREDICATE_NAMES):
                logger.warning(
                    "Dropping triple with out-of-schema predicate",
                    extra={"predicate": pred_label, "page_index": page_index},
                )
                continue
            t.subject.node["patient_id"] = str(getattr(patient, "id", "-1"))
            t.provenance = _provenance_dict(page_index, llm_client)
            filtered_triples.append(t)
    except (TypeError, AttributeError, pydantic.ValidationError, ValueError):
        logger.exception("Could not validate structured triples", extra={"page_index": page_index})
        return []
    else:
        return filtered_triples


def extract_facts_from_pdf(
    pdf_path: str,
    llm_client: BaseChatModel,
    patient=None,
) -> list:
    """
    PDF image-based triple extraction pipeline.
        - Convert PDF pages to images.
        - For each page image, build LLM messages and invoke LLM.
        - Process and validate LLM response as triples.
        - Persist valid triples to DB.
        - Returns all extracted triples across pages.
    """
    structured_llm_client = llm_client.with_structured_output(
        schema=IngestPromptWithContextResponse, method="json_mode"
    )

    images = convert_pages(pdf_path)
    all_triples: list = []
    for i, image_bytes in enumerate(images, start=1):
        base64_img = base64.b64encode(image_bytes).decode("utf-8")
        messages = _build_image_messages(i, base64_img)
        try:
            response = structured_llm_client.invoke(messages)
            triples_to_save = _process_response(response, patient, i, structured_llm_client)
            if triples_to_save:
                all_triples.extend(triples_to_save)
                save_triples(triples_to_save, patient=patient, source_type="pdf")
            continue
        except (ValueError, TypeError, AttributeError, RuntimeError, ConnectionError, TimeoutError, OSError):
            logger.exception("Failed to extract triples", extra={"page_index": i})
            continue
    return all_triples
