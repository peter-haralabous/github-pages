from datetime import date
from typing import Any

from django.forms import ValidationError

from sandwich.core.validators.date_time import not_in_future


def valid_date_of_birth(value: Any) -> date:
    if not isinstance(value, date):
        msg = "Must be a valid date."
        raise ValidationError(msg)
    not_in_future(value)
    return value
