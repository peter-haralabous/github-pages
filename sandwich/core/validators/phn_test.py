import pytest

from sandwich.core.models.patient import ProvinceChoices
from sandwich.core.validators.phn import phn_attr_for_province


@pytest.mark.parametrize(
    ("province_choice", "expected_pattern", "expected_placeholder"),
    [
        (ProvinceChoices.BRITISH_COLUMBIA, r"[9]\d{9}", "10 digits required for BC"),
        (
            ProvinceChoices.ONTARIO,
            r"[1-9]\d{9}[a-zA-Z]{0,2}",
            "10 digits (optional 2 letters added on) required for ON",
        ),
        (ProvinceChoices.QUEBEC, r"[a-zA-Z]{4}\d{8}", "12 characters required for QC"),
        (ProvinceChoices.ALBERTA, r"^\d*$", "Personal Health Number"),
    ],
    ids=["BC", "ON", "QC", "Province besides BC, ON, QC"],
)
def test_phn_attr_returns_correct_dictionary(province_choice, expected_pattern, expected_placeholder):
    """Test that the function returns the correct dictionary structure and values."""

    result = phn_attr_for_province(province_choice)

    assert result["pattern"] == expected_pattern
    assert result["placeholder"] == expected_placeholder
    assert "title" in result
