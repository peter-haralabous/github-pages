import re
from typing import Any

from sandwich.core.models.patient import ProvinceChoices


def phn_attr_for_province(province: str | None) -> dict[str, Any]:
    # More provinces can be added
    # Ref: https://github.com/thrivehealth/allthethings/blob/main/packages/questionnaire/src/validators/phn.ts#L37-L57
    if province == ProvinceChoices.BRITISH_COLUMBIA.value:
        return {
            "placeholder": "10 digits required for BC",
            "pattern": r"[9]\d{9}",
            "title": "First digit must be a 9 followed by 9 digits",
        }
    if province == ProvinceChoices.ONTARIO.value:
        return {
            "placeholder": "10 digits (optional 2 letters added on) required for ON",
            "pattern": r"[1-9]\d{9}[a-zA-Z]{0,2}",
            "title": "10 digits (optional 2 letters added on) required",
        }
    if province == ProvinceChoices.QUEBEC.value:
        return {
            "placeholder": "12 characters required for QC",
            "pattern": r"[a-zA-Z]{4}\d{8}",
            "title": "4 characters followed by 8 digits are required",
        }
    return {
        "placeholder": "Personal Health Number",
        "pattern": r"^\d*$",
        "title": "Only digits required",
    }


def is_valid_bc_phn(phn: str) -> bool:
    """Custom validation for the BC PHN field."""
    trimmed_phn = re.sub(r"[-_\s]", "", phn)
    if not trimmed_phn.isdigit():
        return False
    bc_phn_weight = [0, 2, 4, 8, 5, 10, 9, 7, 3, 0]

    # BC phn pattern validator
    # 1. Ignore the first digit in the PHN since it is always a 9.
    # 2. Multiply each digit (2-9) by its weight and divide each product by 11.
    # 3. Sum the remainder values and divide the total by 11.
    # 4. Subtract the remainder from 11 to yield a check digit value.
    # 5. Compare this value to the 10th digit, and if the two numbers are equal then the PHN is valid,
    # otherwise the PHN is invalid.  If the result is 10 or 11, the PHN is not valid because the 10th digit
    # is a single number.
    # Ref: https://github.com/thrivehealth/allthethings/blob/main/packages/questionnaire/src/validators/phn.ts#L11-L35

    sum_remainder = 0
    sum_remainder = sum((bc_phn_weight[index] * int(digit) % 11 for index, digit in enumerate(trimmed_phn[:9])))
    result = 11 - (sum_remainder % 11)
    if result in {10, 11}:
        return False
    try:
        check_digit = int(trimmed_phn[9])
    except (ValueError, IndexError):
        check_digit = None
    return result == check_digit


def clean_phn(province: ProvinceChoices, phn: str) -> str | None:
    trimmed_phn = re.sub(r"\s+", "", phn)
    if province == ProvinceChoices.BRITISH_COLUMBIA and not is_valid_bc_phn(trimmed_phn):
        return None

    return trimmed_phn
