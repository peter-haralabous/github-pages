from datetime import UTC
from datetime import datetime
from datetime import timedelta
from typing import Any

import pytest
from django.forms import ValidationError

from sandwich.core.validators.date_of_birth import valid_date_of_birth


@pytest.mark.parametrize(
    ("value"),
    [
        pytest.param(
            datetime.strptime("1995-11-23", "%Y-%m-%d").date(),  # noqa: DTZ007
            id="Date in past",
        ),
        pytest.param(
            datetime.now(tz=UTC).date(),
            id="Born today",
        ),
    ],
)
def test_date_of_birth_valid(value: Any) -> None:
    try:
        assert valid_date_of_birth(value)
    except ValidationError:
        pytest.fail("Unexpected validation error")


@pytest.mark.parametrize(
    ("value"),
    [
        pytest.param(
            datetime.strptime("2500-11-23", "%Y-%m-%d").date(),  # noqa: DTZ007
            id="Date in future",
        ),
        pytest.param(
            datetime.now(tz=UTC).date() + timedelta(days=1),
            id="Date in near future",
        ),
        pytest.param(
            "Some bogus string",
            id="Not a valid date object",
        ),
    ],
)
def test_date_of_birth_invalid(value: Any) -> None:
    with pytest.raises(ValidationError):
        valid_date_of_birth(value)
