from pathlib import Path

import pytest

from sandwich.core.service.ingest.extract_pdf import convert_pages
from sandwich.core.service.ingest.extract_pdf import extract_facts_from_pdf
from sandwich.core.service.llm import ModelName
from sandwich.core.service.llm import get_llm


@pytest.mark.skip("pdf -> image conversion isn't stable across platforms so our fixtures are different in CI")
@pytest.mark.vcr
@pytest.mark.django_db
def test_extract_facts_from_pdf(tmp_path):
    pdf_path = "sandwich/core/fixtures/mock_health_data.pdf"
    llm_client = get_llm(ModelName.CLAUDE_SONNET_4_5)
    patient = None
    result = extract_facts_from_pdf(pdf_path, llm_client, patient=patient)
    assert isinstance(result, list)
    # Collect all names and patient nodes
    names = [
        t.obj.node["name"] for t in result if hasattr(t, "obj") and hasattr(t.obj, "node") and "name" in t.obj.node
    ]
    patient_nodes = [
        t.subject.node for t in result if hasattr(t, "subject") and hasattr(t.subject, "node") and t.subject.node
    ]
    # Check immunizations and medications
    assert "Influenza" in names
    assert "COVID-19" in names
    assert "Lisinopril" in names
    assert "Omeprazole" in names
    assert "Hypertension" in names
    assert "GERD" in names

    # Check for at least one patient node with expected demographics (allow partials)
    has_name = any(n.get("first_name") == "Jane" and n.get("last_name") == "Doe" for n in patient_nodes)
    assert has_name, f"Expected patient name not found in any triple: {patient_nodes}"


def test_convert_pages_from_path():
    pdf_path = "sandwich/core/fixtures/mock_health_data.pdf"
    pages = convert_pages(pdf_path)
    assert isinstance(pages, list)
    assert pages, "Expected at least one page image"
    assert isinstance(pages[0], bytes | bytearray)


def test_convert_pages_from_bytes():
    pdf_path = "sandwich/core/fixtures/mock_health_data.pdf"
    with Path(pdf_path).open("rb") as fh:
        pdf_bytes = fh.read()
    pages = convert_pages(pdf_bytes)
    assert isinstance(pages, list)
    assert pages, "Expected at least one page image when passing bytes"
    assert isinstance(pages[0], bytes | bytearray)
    assert isinstance(pages[0], bytes | bytearray)
