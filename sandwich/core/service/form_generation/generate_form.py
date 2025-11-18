import logging
from pathlib import Path
from typing import Any
from typing import cast

import pydantic
from pydantic.fields import Field

from sandwich.core.models.form import Form
from sandwich.core.service.form_generation.prompt import form_from_csv
from sandwich.core.service.form_generation.prompt import form_from_pdf
from sandwich.core.service.llm import ModelName
from sandwich.core.service.llm import get_llm
from sandwich.core.util.procrastinate import define_task

logger = logging.getLogger(__name__)


class SurveySchemaSinglePage(pydantic.BaseModel):
    """
    When using structured output, this model enforces a single page assessment.
    """

    title: str = Field(description="The form name")
    elements: list[dict[str, Any]] = Field(description="The list of form elements.")


class SurveySchemaMultiPage(pydantic.BaseModel):
    """
    When using structured output, this model enforces a multipage assessment.
    """

    title: str = Field(description="The form name")
    pages: list[dict[str, Any]] = Field(description="The list of elements separated into their respective pages.")


class SurveySchema(pydantic.BaseModel):
    """
    When using structured output, this model allows the LLM to decide whether
    a multipage or single page assessment is best.
    """

    title: str = Field(description="The form name")
    pages: list[dict[str, Any]] | None = Field(
        description="List of elements separated into their respective pages. Used at top level for mult-page forms."
    )
    elements: list[dict[str, Any]] | None = Field(
        description="List of form elements. Used at top level for single page forms."
    )


def generate_form_schema_from_bytes(doc_type: str, doc_bytes: bytes, text_prompt: str) -> SurveySchema:
    """
    Generate a form schema from a file.
    """
    llm = get_llm(ModelName.CLAUDE_SONNET_4_5)
    return cast(
        "SurveySchema",
        llm.with_structured_output(SurveySchema).invoke(
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "document": {
                                "name": "form reference file",
                                "format": doc_type,
                                "source": {"bytes": doc_bytes},
                            }
                        },
                        {"text": text_prompt},
                    ],
                }
            ]
        ),
    )


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
        response = generate_form_schema_from_bytes(doc_type="pdf", doc_bytes=file.read(), text_prompt=prompt)

    elif ext == ".csv":
        prompt = form_from_csv(description)
        response = generate_form_schema_from_bytes(doc_type="csv", doc_bytes=file.read(), text_prompt=prompt)

    else:
        raise ValueError(f"Unsupported file type: {file.content_type}")

    # TODO(MM): Add navigation for multipage forms and other defaults
    schema = response.model_dump()
    form.name = response.title
    form.schema = schema
    form.save()
