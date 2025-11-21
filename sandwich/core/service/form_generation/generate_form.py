import base64
import logging
from enum import StrEnum
from io import BytesIO
from pathlib import Path
from typing import Any
from uuid import uuid4

import pydantic
from pydantic.fields import Field
from pypdf import PdfReader
from pypdf import PdfWriter

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


# Adapted from healthbox
def _split_pdf_into_pages(pdf_content: bytes) -> list[bytes]:
    """Split PDF into individual page PDFs and return as bytes."""

    try:
        logger.info("Splitting PDF into individual pages")
        pdf_reader = PdfReader(BytesIO(pdf_content))
        page_pdfs = []

        for page_num in range(len(pdf_reader.pages)):
            # Create a new PDF writer for this page
            pdf_writer = PdfWriter()
            pdf_writer.add_page(pdf_reader.pages[page_num])

            # Write the single page PDF to bytes
            page_buf = BytesIO()
            pdf_writer.write(page_buf)
            page_buf.seek(0)
            page_pdfs.append(page_buf.read())

        return page_pdfs  # noqa: TRY300
    except Exception:
        logger.exception("Error splitting PDF into pages")
        raise


def _invoke_form_gen_agent(form: Form, document: dict, text_prompt: str, thread_id: str) -> None:
    with form_gen_agent(form) as agent:
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
            config=configure(thread_id),
        )


def generate_form_schema_from_reference_file(form: Form, doc_type: DocType, text_prompt: str) -> None:
    """
    Generate a form schema from a file.
    """
    assert form.reference_file, "Form does not have a reference file attached."

    doc_bytes = form.reference_file.read()
    thread_id = f"{form.id!s}_{uuid4()}"

    match doc_type:
        case DocType.PDF:
            pdf_pages = _split_pdf_into_pages(doc_bytes)
            for i in range(len(pdf_pages)):
                page = pdf_pages[i]
                logger.info(
                    "Form generator processing PDF page.",
                    extra={"page_number": i + 1, "file_name": form.reference_file.name},
                )
                document = {
                    "type": "file",
                    "base64": base64.b64encode(page).decode(),
                    "mime_type": "application/pdf",
                    "name": "form_reference_file",
                }
                _invoke_form_gen_agent(form, document, text_prompt, thread_id)

        case DocType.CSV:
            document = {
                "text": f"CSV data: \n{doc_bytes.decode()}",
            }
            _invoke_form_gen_agent(form, document, text_prompt, thread_id)


@define_task
def generate_form_schema(form_id: str, description: str | None = None) -> None:
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
        doc_type = DocType.PDF

    elif ext == ".csv":
        prompt = form_from_csv(description)
        doc_type = DocType.CSV

    else:
        raise ValueError(f"Unsupported file type: {file.content_type}")

    generate_form_schema_from_reference_file(form=form, doc_type=doc_type, text_prompt=prompt)

    # TODO(MM): Add navigation for multipage forms and other defaults
