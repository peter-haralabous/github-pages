import logging
from uuid import UUID

from django.template import loader
from django_eventstream import send_event
from procrastinate.contrib.django import app

from sandwich.core.models import Document
from sandwich.core.service.ingest.extract_pdf import extract_facts_from_pdf
from sandwich.core.service.llm import ModelName
from sandwich.core.service.llm import get_llm

logger = logging.getLogger(__name__)


@app.task
def extract_facts_from_pdf_job(document_id: str, llm_name: str = ModelName.CLAUDE_SONNET_4_5):
    document = Document.objects.get(id=document_id)
    patient = document.patient
    llm_client = get_llm(ModelName(llm_name))
    send_ingest_progress(patient.id, text=f"Processing {document.original_filename}...")

    try:
        with document.file.open("rb") as f:
            pdf_bytes = f.read()
    except Exception:
        logger.exception("Failed to read document file", extra={"document_id": str(document_id)})
        return

    triples = extract_facts_from_pdf(pdf_bytes, llm_client, patient=patient, document=document)
    send_ingest_progress(
        patient.id, text=f"Extracted {len(triples)} facts from {document.original_filename}", done=True
    )


def send_ingest_progress(patient_id: UUID, *, text: str, done=False):
    logger.debug("Sending patient message", extra={"patient_id": patient_id})
    context = {"text": text, "done": done}
    content = loader.render_to_string("patient/partials/ingest_progress.html", context)
    send_event(f"patient/{patient_id}", "ingest_progress", content, json_encode=False)
