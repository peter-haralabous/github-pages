import datetime

from django.core.exceptions import ValidationError
from django.utils import timezone


def not_in_future(value: datetime.date | datetime.datetime) -> None:
    """Validator to ensure a date or datetime is not in the future.

    Using django timezone means we're comparing against the user's timezone
    """
    match type(value):
        case datetime.date:
            if value > timezone.now().date():
                raise ValidationError("Date cannot be in the future.")
        case datetime.datetime:
            if value > timezone.now():
                raise ValidationError("Date/Time cannot be in the future.")
        case _:
            raise ValidationError("Not a Date or Date/Time")
