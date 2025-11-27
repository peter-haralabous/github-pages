import pytest

from sandwich.core.service.medication_service import _extract_medication_results


@pytest.mark.parametrize(
    ("api_results", "expected_medications"),
    [
        pytest.param(
            [
                {"name": "Acetaminophen / Caffeine", "drugbank_pcid": "test_id_123457", "display_name": None},
                {"name": "Acetaminophen [Tylenol]", "drugbank_pcid": "test_id_123456", "display_name": "Tylenol"},
            ],
            [
                {"name": "Acetaminophen / Caffeine", "drugbank_id": "test_id_123457", "display_name": None},
                {"name": "Acetaminophen [Tylenol]", "drugbank_id": "test_id_123456", "display_name": "Tylenol"},
            ],
            id="Map drugbank results to medication results",
        ),
        pytest.param(
            [
                {
                    "name": "Acetaminophen [Tylenol]",
                    "drugbank_pcid": "test_id_123456",
                    "display_name": "Tylenol",
                    "bogus": "this will not make it into the object",
                    "favourite_color": "circle",
                }
            ],
            [{"name": "Acetaminophen [Tylenol]", "drugbank_id": "test_id_123456", "display_name": "Tylenol"}],
            id="MedicationResult only captures relevant info",
        ),
        pytest.param(
            [
                {
                    # no name
                    "drugbank_pcid": "test_id_123456",
                    "display_name": None,
                },
                {
                    # no id
                    "name": "Acetaminophen / Caffeine",
                    "display_name": None,
                },
                {"name": "Acetaminophen [Tylenol]", "drugbank_pcid": "test_id_123456", "display_name": None},
            ],
            [{"name": "Acetaminophen [Tylenol]", "drugbank_id": "test_id_123456", "display_name": None}],
            id="Skip malformed result",
        ),
    ],
)
def test_extract_medication_results(api_results: list[dict], expected_medications: list[dict]) -> None:
    assert expected_medications == _extract_medication_results(api_results)
