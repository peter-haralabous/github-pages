from http import HTTPStatus

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse
from guardian.shortcuts import remove_perm

from sandwich.core.factories.form import FormFactory
from sandwich.core.models import Organization
from sandwich.core.models import Patient
from sandwich.core.models.form import FormStatus
from sandwich.core.models.role import RoleName
from sandwich.core.service.organization_service import assign_organization_role
from sandwich.providers.views.templates import UploadReferenceForm
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
    # The forms shown are only for the org the provider is in, and in descending order by created_at.
    assert response.context["forms"].object_list == [form2, form1]

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


def test_form_template_restore_modal_get_renders_correctly(
    client: Client, provider: User, organization: Organization
) -> None:
    client.force_login(provider)
    assign_organization_role(organization, RoleName.OWNER, provider)
    form = FormFactory.create(organization=organization, schema={"v1": "initial"})
    form.refresh_from_db()
    current_version = form.get_current_version()

    url = reverse(
        "providers:form_template_restore",
        kwargs={"organization_id": organization.id, "form_id": form.id, "form_version_id": current_version.pgh_id},
    )
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK

    assert response.context["form"] == form
    assert response.context["organization"] == organization
    assert response.context["form_version_id"] == current_version.pgh_id


def test_form_template_restore_post_reverts_data(client: Client, provider: User, organization: Organization) -> None:
    client.force_login(provider)
    assign_organization_role(organization, RoleName.OWNER, provider)
    schema_v1 = {"title1": "version1"}
    form = FormFactory.create(organization=organization, schema=schema_v1)
    form.refresh_from_db()
    version_1 = form.get_current_version()

    schema_v2 = {"title2": "version2"}
    form.schema = schema_v2
    form.save()
    form.refresh_from_db()

    assert form.schema == schema_v2

    url = reverse(
        "providers:form_template_restore",
        kwargs={"organization_id": organization.id, "form_id": form.id, "form_version_id": version_1.pgh_id},
    )
    response = client.post(url)

    assert response.status_code == HTTPStatus.FOUND

    expected_redirect = reverse(
        "providers:form_template", kwargs={"organization_id": organization.id, "form_id": form.id}
    )
    assert response["Location"] == expected_redirect

    form.refresh_from_db()
    assert form.schema == schema_v1
    assert form.schema != schema_v2


def test_form_template_restore_deny_access(client: Client, provider: User, organization: Organization) -> None:
    client.force_login(provider)
    form = FormFactory.create()
    form.refresh_from_db()
    version = form.get_current_version()

    url = reverse(
        "providers:form_template_restore",
        kwargs={"organization_id": organization.id, "form_id": form.id, "form_version_id": version.pgh_id},
    )

    response_get = client.get(url)
    assert response_get.status_code == HTTPStatus.NOT_FOUND

    response_post = client.post(url)
    assert response_post.status_code == HTTPStatus.NOT_FOUND


def test_form_generation_success_shows_toast(client: Client, provider: User, organization: Organization) -> None:
    """Test that a successfully generated form shows a success message on next HTMX poll."""
    client.force_login(provider)

    # Create a generating form
    form = FormFactory.create(organization=organization, name="Test Form", status=FormStatus.GENERATING)

    # Simulate HTMX polling with the generating form ID
    url = reverse("providers:form_templates_list", kwargs={"organization_id": organization.id})
    url_with_params = f"{url}?generating_ids={form.id}"

    # Complete the form generation
    form.status = FormStatus.ACTIVE
    form.save()

    # Poll with HTMX request
    response = client.get(url_with_params, HTTP_HX_REQUEST="true")

    assert response.status_code == HTTPStatus.OK
    messages = list(response.context["messages"])
    assert len(messages) == 1
    assert "Test Form" in messages[0].message
    assert "generation successful" in messages[0].message
    assert messages[0].level_tag == "success"


def test_form_generation_failure_shows_toast(client: Client, provider: User, organization: Organization) -> None:
    """Test that a failed form generation shows an error message on next HTMX poll."""
    client.force_login(provider)

    # Create a generating form
    form = FormFactory.create(organization=organization, name="Failed Form", status=FormStatus.GENERATING)

    # Simulate HTMX polling with the generating form ID
    url = reverse("providers:form_templates_list", kwargs={"organization_id": organization.id})
    url_with_params = f"{url}?generating_ids={form.id}"

    # Fail the form generation
    form.status = FormStatus.FAILED
    form.save()

    # Poll with HTMX request
    response = client.get(url_with_params, HTTP_HX_REQUEST="true")

    assert response.status_code == HTTPStatus.OK
    messages = list(response.context["messages"])
    assert len(messages) == 1
    assert "Failed Form" in messages[0].message
    assert "generation failed" in messages[0].message
    assert messages[0].level_tag == "error"


def test_upload_reference_form_rejects_large_files() -> None:
    over_upload_limit = 4.5 * 1024 * 1024 + 1  # 4.5MB + 1
    form = UploadReferenceForm(
        data={
            "name": "Test",
        },
        files={
            "file": SimpleUploadedFile(
                name="large_file.pdf", content=b"a" * int(over_upload_limit), content_type="application/pdf"
            )
        },
    )
    assert not form.is_valid()
    assert "file" in form.errors
    assert form.errors["file"] == ["File cannot be larger than 4.5MB."]


def test_upload_reference_form_rejects_unsupported_files() -> None:
    form = UploadReferenceForm(
        data={
            "name": "Test",
        },
        files={"file": SimpleUploadedFile(name="large_file.png", content=b"content", content_type="image/png")},
    )
    assert not form.is_valid()
    assert "file" in form.errors
    assert form.errors["file"] == ["File extension “png” is not allowed. Allowed extensions are: pdf, csv."]
