import logging
from uuid import UUID

from django.template import loader
from django_eventstream import send_event

from sandwich.core.models import Document
from sandwich.core.service.ingest.extract_pdf import extract_facts_from_pdf
from sandwich.core.service.ingest.extract_records import extract_records
from sandwich.core.service.ingest.extract_text import extract_facts_from_text
from sandwich.core.service.llm import ModelName
from sandwich.core.service.llm import get_llm
from sandwich.core.util.procrastinate import define_task

logger = logging.getLogger(__name__)


@define_task
def process_document_job(document_id: str):
    extract_facts_from_document_job.defer(document_id=document_id)
    extract_records_from_document_job.defer(document_id=document_id)


@define_task
def extract_facts_from_document_job(document_id: str, llm_name: str = ModelName.CLAUDE_SONNET_4_5):
    document = Document.objects.get(id=document_id)
    patient = document.patient
    llm_client = get_llm(ModelName(llm_name))
    send_ingest_progress(patient.id, text=f"Processing {document.original_filename}...")

    try:
        with document.file.open("rb") as f:
            content = f.read()
    except Exception:
        logger.exception("Failed to read document file", extra={"document_id": str(document_id)})
        return

    if document.content_type == "application/pdf":
        triples = extract_facts_from_pdf(content, llm_client, patient=patient, document=document)
    elif document.content_type == "text/plain":
        triples = extract_facts_from_text(content, llm_client, patient=patient, document=document)
    else:
        logger.warning(
            "Unsupported document content type",
            extra={"document_id": str(document_id), "content_type": document.content_type},
        )
        triples = []

    send_ingest_progress(
        patient.id, text=f"Extracted {len(triples)} facts from {document.original_filename}", done=True
    )


@define_task
def extract_records_from_document_job(document_id: str):
    document = Document.objects.get(id=document_id)
    patient = document.patient
    send_ingest_progress(patient.id, text=f"Processing {document.original_filename}...")

    records = extract_records(document)

    send_ingest_progress(
        patient.id, text=f"Extracted {len(records)} records from {document.original_filename}", done=True
    )


def send_ingest_progress(patient_id: UUID, *, text: str, done=False):
    logger.debug("Sending patient message", extra={"patient_id": patient_id})
    context = {"text": text, "done": done}
    content = loader.render_to_string("patient/partials/ingest_progress.html", context)
    send_event(f"patient/{patient_id}", "ingest_progress", content, json_encode=False)
