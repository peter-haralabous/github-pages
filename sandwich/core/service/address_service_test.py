from typing import Any

import pytest

from sandwich.core.service.address_service import extract_address_suggestions


@pytest.mark.parametrize(
    ("response", "expected_addresses"),
    [
        pytest.param({}, [], id="no response data, no suggestions"),
        pytest.param(
            {
                "suggestions": [
                    {"placePrediction": {"text": {"text": "123 Main St, Vancouver, BC"}}},
                    {"placePrediction": {"text": {"text": "456 Another Rd, Vancouver, BC"}}},
                ]
            },
            [
                "123 Main St, Vancouver, BC",
                "456 Another Rd, Vancouver, BC",
            ],
            id="response data, suggestions extracted",
        ),
    ],
)
def test_extract_address_suggestions(response: dict[str, Any], expected_addresses: list[str]) -> None:
    assert extract_address_suggestions(response) == expected_addresses
