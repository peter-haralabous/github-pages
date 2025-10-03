import pytest

from sandwich.providers.views.organization import OrganizationAdd


@pytest.mark.django_db
def test_organization_add_form() -> None:
    form_data = {
        "name": "Test Organization",
        "patient_statuses": '[{"value": "active", "label": "Active"}, {"value": "inactive", "label": "Inactive"}]',
    }
    form = OrganizationAdd(data=form_data)
    assert form.is_valid(), f"Form errors: {form.errors}"
    organization = form.save()
    assert organization.name == "Test Organization"
    assert len(organization.patient_statuses) == 2
    assert organization.patient_statuses[0].value == "active"
    assert organization.patient_statuses[0].label == "Active"
    assert organization.patient_statuses[1].value == "inactive"
    assert organization.patient_statuses[1].label == "Inactive"


@pytest.mark.django_db
def test_organization_add_form_no_statuses() -> None:
    form_data = {
        "name": "Test Organization",
        "patient_statuses": "[]",
    }
    form = OrganizationAdd(data=form_data)
    assert form.is_valid(), f"Form errors: {form.errors}"
    organization = form.save()
    assert organization.name == "Test Organization"
    assert len(organization.patient_statuses) == 0
