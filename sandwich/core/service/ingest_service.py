import logging

from django.db import models
from django.template import loader

from sandwich.core.models import Document
from sandwich.core.models import Patient
from sandwich.core.service.ingest.extract_pdf import extract_facts_from_pdf
from sandwich.core.service.ingest.extract_records import extract_records
from sandwich.core.service.ingest.extract_text import extract_facts_from_text
from sandwich.core.service.llm import ModelName
from sandwich.core.service.llm import get_llm
from sandwich.core.service.sse_service import EventType
from sandwich.core.service.sse_service import sse_patient_channel
from sandwich.core.service.sse_service import sse_send
from sandwich.core.util.procrastinate import define_task

logger = logging.getLogger(__name__)


class ProcessDocumentContext(models.TextChoices):
    PATIENT_CHAT = "patient_chat"


@define_task
def process_document_job(document_id: str, document_context: ProcessDocumentContext | None = None):
    extract_facts_from_document_job.defer(document_id=document_id)
    extract_records_from_document_job.defer(document_id=document_id, document_context=document_context)


@define_task
def extract_facts_from_document_job(document_id: str, llm_name: str = ModelName.CLAUDE_SONNET_4_5):
    document = Document.objects.get(id=document_id)
    patient = document.patient
    llm_client = get_llm(ModelName(llm_name))
    send_ingest_progress(patient, text=f"Processing {document.original_filename}...")

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

    send_ingest_progress(patient, text=f"Extracted {len(triples)} facts from {document.original_filename}", done=True)


@define_task
def extract_records_from_document_job(document_id: str, document_context: ProcessDocumentContext | None = None):
    from sandwich.core.service.chat_service.chat import ChatContext  # noqa: PLC0415
    from sandwich.core.service.chat_service.chat import FileUploadEvent  # noqa: PLC0415
    from sandwich.core.service.chat_service.chat import receive_chat_event  # noqa: PLC0415

    document = Document.objects.get(id=document_id)
    patient = document.patient
    send_ingest_progress(patient, text=f"Processing {document.original_filename}...")

    records = extract_records(document)

    send_ingest_progress(
        patient, text=f"Extracted {len(records)} records from {document.original_filename}", done=True
    )
    if document_context and document_context == ProcessDocumentContext.PATIENT_CHAT:
        receive_chat_event(
            FileUploadEvent(
                context=ChatContext(patient_id=str(patient.id)),
                document_id=str(document.id),
                document_filename=document.original_filename,
                records=records,
            )
        )


def send_ingest_progress(patient: Patient, *, text: str, done=False):
    logger.debug("Sending patient message", extra={"patient_id": str(patient.id)})
    context = {"text": text, "done": done}
    content = loader.render_to_string("patient/partials/ingest_progress.html", context)
    sse_send(sse_patient_channel(patient), EventType.INGEST_PROGRESS, content)
