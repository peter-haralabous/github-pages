from http import HTTPStatus

from django.test import Client
from django.urls import reverse

from sandwich.core.factories.form import FormFactory
from sandwich.core.models.form import Form
from sandwich.core.models.organization import Organization
from sandwich.users.models import User


def test_provider_form_create(client: Client, owner: User, organization: Organization):
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


def test_provider_form_create_validation(client: Client, owner: User, organization: Organization):
    """If the user does not provide a form title, endpoint returns 400 error."""
    client.force_login(owner)
    payload = {"width": "1000px"}
    url = reverse("providers:providers-api:create_form", kwargs={"organization_id": organization.id})
    response = client.post(url, data=payload, content_type="application/json")

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Form must include a title: 'General' section missing 'Survey title'"


def test_provider_form_create_duplicate_form_name(client: Client, owner: User, organization: Organization):
    """Creating a form with the same as an existing one in the organization returns 400 error."""
    existing_form = FormFactory.create(organization=organization, name="Intake Form")

    client.force_login(owner)
    payload = {"title": existing_form.name}
    url = reverse("providers:providers-api:create_form", kwargs={"organization_id": organization.id})
    response = client.post(url, data=payload, content_type="application/json")

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Form with same title already exists. Please choose a different title."
