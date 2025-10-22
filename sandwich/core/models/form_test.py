import pytest
from django.db import IntegrityError

from sandwich.core.models import Organization
from sandwich.core.models.form import Form


def test_form_create(db, organization: Organization) -> None:
    form = Form.objects.create(name="Test Form", schema={"foo": "bar"}, organization=organization)
    assert form.pk is not None
    assert form.name == "Test Form"
    assert form.schema == {"foo": "bar"}
    assert form.organization == organization

    with pytest.raises(IntegrityError):
        # Duplicate form name in same org raises error.
        Form.objects.create(name="Test Form", schema={"baz": "zooka"}, organization=organization)
