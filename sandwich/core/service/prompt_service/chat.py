from typing import TYPE_CHECKING

from langchain_core.prompts import ChatPromptTemplate

from sandwich.core.models import Document
from sandwich.core.service.prompt_service.template import template_contents
from sandwich.core.service.template_service import ContextDict

if TYPE_CHECKING:
    from sandwich.core.service.chat_service.chat import FileUploadEvent


chat_template = ChatPromptTemplate(
    [
        ("system", template_contents("system.md", "system_chat.md")),
    ]
)


def patient_context(patient):
    """Hydrate the patient context template with patient data."""
    return template_contents("patient_context.md").format(
        patient_full_name=patient.full_name,
        patient_date_of_birth=patient.date_of_birth,
        patient_province=patient.province or "Unknown",
    )


def user_context(user):
    """Hydrate the user context template with user data."""
    return template_contents("user_context.md").format(user_full_name=user.get_full_name())


document_upload_template = ChatPromptTemplate(
    [
        ("system", template_contents("document_upload.md")),
    ]
)


def file_upload_context(event: "FileUploadEvent") -> ContextDict:
    document = Document.objects.get(pk=event.document_id)
    return {
        "file_id": str(document.pk),
        "file_name": document.original_filename,
        "file_size": document.size,
        "file_type": document.content_type,
        "file_date": document.date.strftime("%Y-%m-%d") if document.date else "Unknown",
        "file_category": document.category,
        "records_json": event.records.model_dump_json(indent=2),
    }
