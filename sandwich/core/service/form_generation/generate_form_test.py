from pathlib import Path
from uuid import uuid4

import pytest

from sandwich.core.service.form_generation.generate_form import DocType
from sandwich.core.service.form_generation.generate_form import generate_form_schema_from_bytes
from sandwich.core.service.form_generation.prompt import form_from_csv
from sandwich.core.service.form_generation.prompt import form_from_pdf


@pytest.mark.vcr
def test_generate_form_schema_simple_pdf() -> None:
    pdf_bytes = Path("sandwich/core/fixtures/simple_pdf_form.pdf").read_bytes()
    thread_id = str(uuid4())

    prompt = form_from_pdf()
    response = generate_form_schema_from_bytes(
        doc_type=DocType.PDF, doc_bytes=pdf_bytes, text_prompt=prompt, thread_id=thread_id
    )
    assert response.title == "Simple Form"
    assert response.elements
    assert response.elements[0].get("type") == "text"
    assert response.elements[0].get("title") == "First name"


@pytest.mark.vcr
def test_generate_form_schema_simple_csv() -> None:
    csv_bytes = b"""
    title,Simple Form
    q1, First name, textfield
    """

    thread_id = str(uuid4())
    prompt = form_from_csv()
    response = generate_form_schema_from_bytes(
        doc_type=DocType.CSV, doc_bytes=csv_bytes, text_prompt=prompt, thread_id=thread_id
    )
    assert response.title == "Simple Form"
    assert response.elements
    assert response.elements[0].get("type") == "text"
    assert response.elements[0].get("title") == "First name"
