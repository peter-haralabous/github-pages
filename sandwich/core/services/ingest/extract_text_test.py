import pytest

from sandwich.core.services.ingest.extract_text import extract_facts_from_text


@pytest.mark.vcr
def test_extract_facts_from_text():
    input_text = "Jane has a fever and a cough."
    triples = extract_facts_from_text(input_text)
    assert len(triples) > 0
    assert triples[0].subject.node["name"] == "Jane"
    assert triples[0].obj.node["name"] in {"Fever", "Cough"}


@pytest.mark.vcr
def test_extract_single_symptom():
    input_text = "John has a headache."
    triples = extract_facts_from_text(input_text)
    assert len(triples) > 0
    assert triples[0].subject.node["name"] == "John"
    assert triples[0].obj.node["name"] == "Headache"


@pytest.mark.vcr
def test_extract_medication():
    input_text = "Alice is taking ibuprofen."
    triples = extract_facts_from_text(input_text)
    assert len(triples) > 0
    assert triples[0].subject.node["name"] == "Alice"
    assert "ibuprofen" in str(triples[0].obj.node["name"])


@pytest.mark.vcr
def test_extract_no_facts():
    input_text = "The sky is blue."
    triples = extract_facts_from_text(input_text)
    assert triples == []
