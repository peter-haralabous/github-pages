from typing import TYPE_CHECKING

from django.template import Context
from django.template import Engine
from langchain_core.prompts import ChatPromptTemplate

from sandwich.core.models import Document
from sandwich.core.service.prompt_service.template import template_contents
from sandwich.core.service.template_service import ContextDict

if TYPE_CHECKING:
    from sandwich.core.service.chat_service.event import FileProcessedEvent

chat_template = ChatPromptTemplate(
    [
        ("system", template_contents("system.md", "system_chat.md")),
    ]
)


def patient_context(patient):
    """Hydrate the patient context template with patient data."""
    template = Engine().from_string(template_code=template_contents("patient_context.md"))
    return template.render(
        Context(
            {
                "patient_full_name": patient.full_name,
                "patient_date_of_birth": patient.date_of_birth,
                "patient_province": patient.province or "Unknown",
                "phn": patient.phn,
                "email": patient.email,
            }
        )
    )


def patient_record_context(patient):
    """Hydrate the patient record template with patient data."""

    template = Engine().from_string(template_code=template_contents("patient_record_context.md"))
    context = Context(
        {
            "immunizations": list(patient.immunization_set.all().order_by("-date")),
            "practitioners": list(patient.practitioner_set.all()),
            "conditions": list(patient.condition_set.all().order_by("-onset")),
        }
    )

    # render the template with the context
    return template.render(context)


def patient_summary_system(patient):
    """Hydrate the patient summary system template with patient data."""

    template = Engine().from_string(template_code=template_contents("patient_summary_system.md"))
    context = Context(
        {
            "patient_context": f"{patient_context(patient)}\n\n{patient_record_context(patient)}",
        }
    )

    return template.render(context)


def user_context(user):
    """Hydrate the user context template with user data."""
    return template_contents("user_context.md").format(user_full_name=user.get_full_name())


file_processed_template = ChatPromptTemplate(
    [
        ("system", template_contents("document_processed.md")),
    ]
)


def file_processed_context(event: "FileProcessedEvent") -> ContextDict:
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
