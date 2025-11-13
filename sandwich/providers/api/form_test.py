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


def test_create_form(client: Client, owner: User, organization: Organization):
    orgs_forms = Form.objects.filter(organization=organization)
    assert orgs_forms.exists() is False

    client.force_login(owner)
    payload = {"title": "Intake Form"}
    url = reverse("providers:providers-api:create_form", kwargs={"organization_id": organization.id})
    response = client.post(url, data=payload, content_type="application/json")

    created_form = orgs_forms.first()
    assert created_form is not None
    assert response.status_code == HTTPStatus.OK
    assert response.json()["form_id"] == str(created_form.id)
    assert response.json()["message"] == "Form created successfully"


def test_create_form_validation(client: Client, owner: User, organization: Organization):
    """If the user does not provide a form title, endpoint returns 400 error."""
    client.force_login(owner)
    payload = {"width": "1000px"}
    url = reverse("providers:providers-api:create_form", kwargs={"organization_id": organization.id})
    response = client.post(url, data=payload, content_type="application/json")

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Form must include a title: 'General' section missing 'Survey title'"


def test_create_form_duplicate_form_name(client: Client, owner: User, organization: Organization, intake_form: Form):
    """Creating a form with the same as an existing one in the organization returns 400 error."""
    client.force_login(owner)
    payload = {"title": intake_form.name}
    url = reverse("providers:providers-api:create_form", kwargs={"organization_id": organization.id})
    response = client.post(url, data=payload, content_type="application/json")

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Form with the same title already exists. Please choose a different title."


def test_edit_form(client: Client, owner: User, organization: Organization, intake_form: Form):
    client.force_login(owner)
    payload = {"title": "Intake"}
    url = reverse(
        "providers:providers-api:edit_form", kwargs={"organization_id": organization.id, "form_id": intake_form.id}
    )
    response = client.post(url, data=payload, content_type="application/json")

    intake_form.refresh_from_db()
    assert response.status_code == HTTPStatus.OK
    assert response.json()["form_id"] == str(intake_form.id)
    assert response.json()["message"] == "Form saved successfully"
    assert intake_form.name == "Intake"
    assert intake_form.schema == payload


def test_edit_form_validation(client: Client, owner: User, organization: Organization, intake_form: Form):
    """If the user deletes the form's title, endpoint returns 400 error."""
    client.force_login(owner)
    payload = {"width": "1000px"}  # no title in payload
    url = reverse(
        "providers:providers-api:edit_form", kwargs={"organization_id": organization.id, "form_id": intake_form.id}
    )
    response = client.post(url, data=payload, content_type="application/json")

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Form must include a title: 'General' section missing 'Survey title'"


def test_edit_form_duplicate_form_name(client: Client, owner: User, organization: Organization, intake_form: Form):
    """If the user changes the form title to an existing form in their org, endpoint returns 400 error."""
    form1 = FormFactory.create(organization=organization, name="Intake (Copy)")
    client.force_login(owner)
    payload = {"title": intake_form.name}
    url = reverse(
        "providers:providers-api:edit_form", kwargs={"organization_id": organization.id, "form_id": form1.id}
    )
    response = client.post(url, data=payload, content_type="application/json")

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Form with the same title already exists. Please choose a different title."
