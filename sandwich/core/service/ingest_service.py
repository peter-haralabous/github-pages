import logging

from procrastinate.contrib.django import app

from sandwich.core.models import Document
from sandwich.core.service.ingest.extract_pdf import extract_facts_from_pdf
from sandwich.core.service.llm import ModelName
from sandwich.core.service.llm import get_llm

logger = logging.getLogger(__name__)


@app.task
def extract_facts_from_pdf_job(document_id: str, llm_name: str = ModelName.CLAUDE_SONNET_4_5):
    document = Document.objects.get(id=document_id)
    patient = document.patient if hasattr(document, "patient") else None
    llm_client = get_llm(ModelName(llm_name))

    try:
        with document.file.open("rb") as f:
            pdf_bytes = f.read()
    except Exception:
        logger.exception("Failed to read document file", extra={"document_id": str(document_id)})
        return

    extract_facts_from_pdf(pdf_bytes, llm_client, patient=patient)
