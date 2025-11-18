from pathlib import Path

import pytest

from sandwich.core.service.form_generation.generate_form import generate_form_schema_from_bytes
from sandwich.core.service.form_generation.prompt import form_from_csv
from sandwich.core.service.form_generation.prompt import form_from_pdf


@pytest.mark.vcr
def test_generate_form_schema_simple_pdf() -> None:
    pdf_bytes = Path("sandwich/core/fixtures/simple_pdf_form.pdf").read_bytes()

    prompt = form_from_pdf()
    response = generate_form_schema_from_bytes(doc_type="pdf", doc_bytes=pdf_bytes, text_prompt=prompt)
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

    prompt = form_from_csv()
    response = generate_form_schema_from_bytes(doc_type="csv", doc_bytes=csv_bytes, text_prompt=prompt)
    assert response.title == "Simple Form"
    assert response.elements
    assert response.elements[0].get("type") == "text"
    assert response.elements[0].get("title") == "First name"
