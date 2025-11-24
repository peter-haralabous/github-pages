from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse

from sandwich.core.factories.form import FormFactory
from sandwich.core.models.form import Form
from sandwich.core.models.organization import Organization
from sandwich.users.models import User


@pytest.fixture
def intake_form(organization: Organization) -> Form:
    return FormFactory.create(organization=organization, name="Intake Form")


def test_save_form_handles_create(client: Client, owner: User, organization: Organization) -> None:
    orgs_forms = Form.objects.filter(organization=organization)
    assert orgs_forms.exists() is False

    client.force_login(owner)
    payload = {"schema": {"title": "Intake Form"}, "form_id": None}  # when form_id is None, create form.
    url = reverse("providers:providers-api:save_form", kwargs={"organization_id": organization.id})
    response = client.post(url, data=payload, content_type="application/json")

    created_form = orgs_forms.first()
    assert created_form is not None
    assert response.status_code == HTTPStatus.OK
    assert response.json()["form_id"] == str(created_form.id)
    assert response.json()["message"] == "Form saved successfully"


def test_save_form_handles_edit(client: Client, owner: User, organization: Organization, intake_form: Form) -> None:
    client.force_login(owner)
    updated_form_name = "Intake"
    payload = {"schema": {"title": updated_form_name}, "form_id": intake_form.id}
    url = reverse("providers:providers-api:save_form", kwargs={"organization_id": organization.id})
    response = client.post(url, data=payload, content_type="application/json")

    assert response.status_code == HTTPStatus.OK
    intake_form.refresh_from_db()
    assert response.json()["form_id"] == str(intake_form.id)
    assert response.json()["message"] == "Form saved successfully"
    assert intake_form.name == updated_form_name


def test_save_form_no_form_name(client: Client, owner: User, organization: Organization) -> None:
    """If the user deletes the form's title on edit or doesn't supply it on create, endpoint returns 400 error."""
    client.force_login(owner)
    payload = {"schema": {"width": "1000px"}, "form_id": None}  # no title in payload.schema
    url = reverse("providers:providers-api:save_form", kwargs={"organization_id": organization.id})
    response = client.post(url, data=payload, content_type="application/json")

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Form must include a title: 'General' section missing 'Survey title'"


def test_save_form_duplicate_form_name(client: Client, owner: User, organization: Organization, intake_form: Form):
    """If the form title matches an existing form in the org, endpoint returns 400 error."""
    form1 = FormFactory.create(organization=organization, name="Intake (Copy)")
    client.force_login(owner)
    payload = {"schema": {"title": intake_form.name}, "form_id": form1.id}
    url = reverse("providers:providers-api:save_form", kwargs={"organization_id": organization.id})
    response = client.post(url, data=payload, content_type="application/json")

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Form with this Organization and Name already exists."
    form1.refresh_from_db()
    assert form1.name == "Intake (Copy)"  # name unchanged
