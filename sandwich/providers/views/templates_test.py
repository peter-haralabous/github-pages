from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from guardian.shortcuts import remove_perm

from sandwich.core.factories.form import FormFactory
from sandwich.core.models import Organization
from sandwich.core.models import Patient
from sandwich.core.models.role import RoleName
from sandwich.users.models import User


def test_form_list(client: Client, provider: User, organization: Organization) -> None:
    client.force_login(provider)
    url = reverse("providers:form_templates_list", kwargs={"organization_id": organization.id})
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert "provider/form_list.html" in [t.name for t in response.templates]


def test_form_list_user_not_in_organization_deny_access(
    client: Client, user: User, organization: Organization
) -> None:
    client.force_login(user)
    url = reverse("providers:form_templates_list", kwargs={"organization_id": organization.id})
    response = client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_form_list_filters_allowed_forms(client: Client, provider: User, organization: Organization) -> None:
    """Only forms belonging to the organization are shown to a provider.

    And only forms that a provider has view_form permission for are shown.
    """
    # Add a form for another organization
    FormFactory.create(name="Org2 Form")

    # Add a couple for this provider's organization.
    form1 = FormFactory.create(organization=organization, name="Form 1")
    form2 = FormFactory.create(organization=organization, name="Form 2")

    client.force_login(provider)
    url = reverse("providers:form_templates_list", kwargs={"organization_id": organization.id})
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    # The forms shown are only for the org the provider is in.
    assert response.context["forms"].object_list == [form1, form2]

    # Remove form2's view_form permission from the provider group to demonstrate that it would not be shown.
    provider_group = organization.get_role(RoleName.STAFF).group
    remove_perm("view_form", provider_group, form2)

    url = reverse("providers:form_templates_list", kwargs={"organization_id": organization.id})
    response = client.get(url)
    # Only form1 is shown now.
    assert response.context["forms"].object_list == [form1]


def test_form_details(client: Client, provider: User, organization: Organization) -> None:
    form = FormFactory.create(organization=organization)
    client.force_login(provider)
    url = reverse("providers:form_template", kwargs={"organization_id": organization.id, "form_id": form.id})
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert "provider/form_details.html" in [t.name for t in response.templates]


def test_form_details_user_not_in_organization_deny_access(
    client: Client, user: User, organization: Organization
) -> None:
    form = FormFactory.create(organization=organization)
    client.force_login(user)
    url = reverse("providers:form_template", kwargs={"organization_id": organization.id, "form_id": form.id})
    response = client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_form_details_patient_deny_access(client: Client, patient: Patient, organization: Organization) -> None:
    """Patient in org cannot access provider's view of a form template."""
    form = FormFactory.create(organization=organization)
    assert patient.user is not None
    client.force_login(patient.user)
    url = reverse("providers:form_template", kwargs={"organization_id": organization.id, "form_id": form.id})
    response = client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_form_builder_deny_staff_access(client: Client, provider: User, organization: Organization) -> None:
    client.force_login(provider)
    url = reverse("providers:form_template_builder", kwargs={"organization_id": organization.id})
    response = client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_form_builder(client: Client, owner: User, organization: Organization) -> None:
    client.force_login(owner)
    url = reverse("providers:form_template_builder", kwargs={"organization_id": organization.id})
    response = client.get(url)
    created_form = organization.form_set.order_by("-created_at").first()
    assert created_form is not None
    assert response.status_code == HTTPStatus.FOUND
    expected_url = reverse(
        "providers:form_template_edit", kwargs={"organization_id": organization.id, "form_id": created_form.id}
    )
    assert response.url == expected_url  # type: ignore[attr-defined]


def test_form_template_preview(client: Client, provider: User, organization: Organization) -> None:
    form = FormFactory.create(organization=organization)
    form_version = form.get_current_version()
    client.force_login(provider)
    url = reverse(
        "providers:form_template_preview",
        kwargs={"organization_id": organization.id, "form_id": form.id, "form_version_id": form_version.pgh_id},
    )
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_form_template_preview_deny_access(client: Client, provider: User, organization: Organization) -> None:
    form = FormFactory.create()
    form_version = form.get_current_version()
    client.force_login(provider)
    url = reverse(
        "providers:form_template_preview",
        kwargs={"organization_id": organization.id, "form_id": form.id, "form_version_id": form_version.pgh_id},
    )
    response = client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_form_template_preview_older_versions(client: Client, provider: User, organization: Organization) -> None:
    client.force_login(provider)
    original_schema = {"title": "form_version_1"}
    form = FormFactory.create(organization=organization, schema=original_schema)

    form.refresh_from_db()
    version_1 = form.get_current_version()

    assert version_1.schema == original_schema

    updated_schema = {"title": "form_version_2"}
    form.schema = updated_schema
    form.save()

    form.refresh_from_db()
    version_2 = form.get_current_version()

    assert version_2.schema == updated_schema
    assert version_1.pgh_id != version_2.pgh_id

    # Get url of older version of form
    url = reverse(
        "providers:form_template_preview",
        kwargs={"organization_id": organization.id, "form_id": form.id, "form_version_id": version_1.pgh_id},
    )
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK

    assert response.context["form_schema"] == original_schema
    assert response.context["form_schema"] != updated_schema
