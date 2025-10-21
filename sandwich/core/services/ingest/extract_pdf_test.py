import pytest

from sandwich.core.service.llm import ModelName
from sandwich.core.service.llm import get_llm
from sandwich.core.services.ingest.extract_pdf import extract_facts_from_pdf


@pytest.mark.vcr
@pytest.mark.django_db
def test_extract_facts_from_pdf(tmp_path):
    pdf_path = "sandwich/core/fixtures/mock_health_data.pdf"
    llm_client = get_llm(ModelName.CLAUDE_3_SONNET)
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
    assert "Influenza Vaccine" in names
    assert "COVID-19 Vaccine" in names
    assert "Shingrix Vaccine" in names
    assert "Lisinopril" in names
    assert "Omeprazole" in names
    assert "Multivitamin" in names
    assert "Ibuprofen" in names
    # Check for at least one patient node with expected demographics (allow partials)
    has_name = any(n.get("first_name") == "Jane" and n.get("last_name") == "Doe" for n in patient_nodes)
    assert has_name, f"Expected patient name not found in any triple: {patient_nodes}"
