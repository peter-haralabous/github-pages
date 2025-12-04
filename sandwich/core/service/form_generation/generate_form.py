import base64
import logging
from enum import StrEnum
from pathlib import Path
from typing import Any

import pydantic
from pydantic.fields import Field

from sandwich.core.models.form import Form
from sandwich.core.service.agent_service.config import configure
from sandwich.core.service.form_generation.agent import form_gen_agent
from sandwich.core.service.form_generation.prompt import form_from_csv
from sandwich.core.service.form_generation.prompt import form_from_pdf
from sandwich.core.util.procrastinate import define_task

logger = logging.getLogger(__name__)


class SurveySchema(pydantic.BaseModel):
    """
    When using structured output, this model allows the LLM to decide whether
    a multipage or single page assessment is best.
    """

    title: str = Field(description="The form name")
    pages: list[dict[str, Any]] | None = Field(
        description="List of elements separated into their respective pages. Used at top level for multipage forms."
    )
    elements: list[dict[str, Any]] | None = Field(
        description="List of form elements. Used at top level for single page forms."
    )


class DocType(StrEnum):
    PDF = "pdf"
    CSV = "csv"


def generate_form_schema_from_bytes(
    doc_type: DocType, doc_bytes: bytes, text_prompt: str, thread_id: str
) -> SurveySchema:
    """
    Generate a form schema from a file.
    """
    match doc_type:
        case DocType.PDF:
            document = {
                "type": "file",
                "base64": base64.b64encode(doc_bytes).decode(),
                "mime_type": "application/pdf",
                "name": "form_reference_file",
            }
        case DocType.CSV:
            document = {
                "text": f"CSV data: \n{doc_bytes.decode()}",
            }

    with form_gen_agent() as agent:
        return agent.invoke(
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
            config=configure(thread_id),
        )["structured_response"]


@define_task
def generate_form_schema_from_reference_file(form_id: str, description: str | None = None) -> None:
    """
    Entry for PDF/CSV -> SurveyJS form schema generation.
    """

    form = Form.objects.get(id=form_id)
    file = form.reference_file
    ext = Path(file.name).suffix

    # TODO(MM): Process multipage PDFs one page at a time.The current
    # implementation times out with large, multipage PDFs.
    if ext == ".pdf":
        prompt = form_from_pdf(description)
        response = generate_form_schema_from_bytes(
            doc_type=DocType.PDF, doc_bytes=file.read(), text_prompt=prompt, thread_id=str(form.id)
        )

    elif ext == ".csv":
        prompt = form_from_csv(description)
        response = generate_form_schema_from_bytes(
            doc_type=DocType.CSV, doc_bytes=file.read(), text_prompt=prompt, thread_id=str(form.id)
        )

    else:
        raise ValueError(f"Unsupported file type: {file.content_type}")

    # TODO(MM): Add navigation for multipage forms and other defaults
    schema = response.model_dump()
    form.name = response.title
    form.schema = schema
    form.save()
