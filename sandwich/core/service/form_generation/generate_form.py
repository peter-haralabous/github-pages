import base64
import logging
from enum import StrEnum
from pathlib import Path
from uuid import uuid4

from langgraph.graph.state import RunnableConfig

from sandwich.core.models.form import Form
from sandwich.core.models.form import FormStatus
from sandwich.core.service.agent_service.config import configure
from sandwich.core.service.form_generation.agent import form_gen_agent
from sandwich.core.service.form_generation.prompt import form_from_csv
from sandwich.core.service.form_generation.prompt import form_from_pdf
from sandwich.core.util.procrastinate import define_task

logger = logging.getLogger(__name__)


class DocType(StrEnum):
    PDF = "pdf"
    CSV = "csv"


def generate_form_schema_from_reference_file(form: Form, doc_type: DocType, text_prompt: str) -> None:
    """
    Generate a form schema from a file.
    """
    assert form.reference_file, "Form does not have a reference file attached."

    doc_bytes = form.reference_file.read()
    thread_id = f"{form.id!s}_{uuid4()}"
    # NB: Default is 25 which is too low for some complex forms. 100 was
    # arbitrarily chosen to give us more headroom -- adjust as needed.
    agent_recursion_limit = 100

    with form_gen_agent(form) as agent:
        if doc_type == DocType.PDF:
            document = {
                "type": "file",
                "base64": base64.b64encode(doc_bytes).decode(),
                "mime_type": "application/pdf",
                "name": "form_reference_file",
            }

        elif doc_type == DocType.CSV:
            document = {
                "text": f"CSV data: \n{doc_bytes.decode()}",
            }

        if not document:
            logger.error(
                "[Form generation] a document was not provided.",
                extra={
                    "form_id": form.id,
                },
            )
            raise ValueError("Must provide a document.")

        agent.invoke(
            input={
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"text": text_prompt},
                            document,
                        ],
                    }
                ]
            },
            config=configure(thread_id, config=RunnableConfig(recursion_limit=agent_recursion_limit)),
        )


@define_task
def generate_form_schema(form_id: str, description: str | None = None) -> None:
    """
    Entry for PDF/CSV -> SurveyJS form schema generation.
    """
    form = Form.objects.get(id=form_id)
    file = form.reference_file
    ext = Path(file.name).suffix

    if ext == ".pdf":
        prompt = form_from_pdf(description)
        doc_type = DocType.PDF

    elif ext == ".csv":
        prompt = form_from_csv(description)
        doc_type = DocType.CSV

    else:
        raise ValueError(f"Unsupported file type: {file.content_type}")

    try:
        generate_form_schema_from_reference_file(form=form, doc_type=doc_type, text_prompt=prompt)
        form.refresh_from_db()
        form.status = FormStatus.ACTIVE
        logger.info("Form generation completed successfully", extra={"form_id": form_id, "form_name": form.name})

    except Exception as e:
        form.status = FormStatus.FAILED
        error_msg = str(e)
        logger.exception(
            "Form generation failed", extra={"form_id": form_id, "form_name": form.name, "error": error_msg}
        )

    form.save()
