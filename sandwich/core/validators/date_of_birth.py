from datetime import date
from typing import Any

from django.forms import ValidationError
from django.utils import timezone


def valid_date_of_birth(value: Any) -> date:
    if not isinstance(value, date):
        msg = "Must be a valid date."
        raise ValidationError(msg)

    # Using django timezone means we're comparing against the user's timezone
    if value > timezone.now().date():
        msg = "Date cannot be in the future."
        raise ValidationError(msg)

    return value
