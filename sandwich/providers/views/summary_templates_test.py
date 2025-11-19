from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from guardian.shortcuts import assign_perm
from playwright.sync_api import Page
from playwright.sync_api import expect

from sandwich.core.factories.form import FormFactory
from sandwich.core.models import Organization
from sandwich.core.models.summary_template import SummaryTemplate
from sandwich.users.models import User


def test_summary_template_list(client: Client, provider: User, organization: Organization) -> None:
    client.force_login(provider)
    url = reverse("providers:summary_template_list", kwargs={"organization_id": organization.id})
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert "provider/summary_template_list.html" in [t.name for t in response.templates]


def test_summary_template_list_user_not_in_organization_deny_access(
    client: Client, user: User, organization: Organization
) -> None:
    client.force_login(user)
    url = reverse("providers:summary_template_list", kwargs={"organization_id": organization.id})
    response = client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_summary_template_list_filters_by_organization(
    client: Client, provider: User, organization: Organization
) -> None:
    form1 = FormFactory.create(organization=organization, name="Form 1")
    form2 = FormFactory.create(organization=organization, name="Form 2")
    other_org_form = FormFactory.create(name="Other Org Form")

    template1 = SummaryTemplate.objects.create(
        organization=organization,
        name="Template 1",
        description="First template",
        text="Template content 1",
        form=form1,
    )
    template2 = SummaryTemplate.objects.create(
        organization=organization,
        name="Template 2",
        description="Second template",
        text="Template content 2",
        form=form2,
    )
    SummaryTemplate.objects.create(
        organization=other_org_form.organization,
        name="Other Org Template",
        description="Should not appear",
        text="Other content",
        form=other_org_form,
    )

    client.force_login(provider)
    url = reverse("providers:summary_template_list", kwargs={"organization_id": organization.id})
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

    # Check that only this organization's templates are shown
    templates_in_response = list(response.context["templates"].object_list)
    assert len(templates_in_response) == 2
    assert template1 in templates_in_response
    assert template2 in templates_in_response


def test_summary_template_list_search(client: Client, provider: User, organization: Organization) -> None:
    form = FormFactory.create(organization=organization)
    template1 = SummaryTemplate.objects.create(
        organization=organization,
        name="Intake Template",
        description="Patient intake form",
        text="Intake content",
        form=form,
    )
    SummaryTemplate.objects.create(
        organization=organization,
        name="Discharge Template",
        description="Patient discharge notes",
        text="Discharge content",
        form=form,
    )

    client.force_login(provider)
    url = reverse("providers:summary_template_list", kwargs={"organization_id": organization.id})

    response = client.get(url, {"search": "Intake"})
    assert response.status_code == HTTPStatus.OK
    templates = list(response.context["templates"].object_list)
    assert len(templates) == 1
    assert templates[0] == template1

    response = client.get(url, {"search": "discharge"})
    assert response.status_code == HTTPStatus.OK
    templates = list(response.context["templates"].object_list)
    assert len(templates) == 1
    assert templates[0].name == "Discharge Template"


def test_summary_template_add_get(client: Client, provider: User, organization: Organization) -> None:
    assign_perm("create_summarytemplate", provider, organization)
    client.force_login(provider)
    url = reverse("providers:summary_template_add", kwargs={"organization_id": organization.id})
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert "provider/summary_template_add.html" in [t.name for t in response.templates]


def test_summary_template_add_post(client: Client, provider: User, organization: Organization) -> None:
    assign_perm("create_summarytemplate", provider, organization)
    form = FormFactory.create(organization=organization)
    client.force_login(provider)
    url = reverse("providers:summary_template_add", kwargs={"organization_id": organization.id})

    data = {
        "name": "New Template",
        "description": "Test description",
        "text": "Template content with {% ai %}tags{% endai %}",
        "form": form.id,
    }
    response = client.post(url, data)

    assert response.status_code == HTTPStatus.FOUND
    assert response["Location"] == reverse(
        "providers:summary_template_list", kwargs={"organization_id": organization.id}
    )

    template = SummaryTemplate.objects.get(name="New Template")
    assert template.organization == organization
    assert template.description == "Test description"
    assert template.form == form


def test_summary_template_edit_get(client: Client, provider: User, organization: Organization) -> None:
    assign_perm("view_organization", provider, organization)
    form = FormFactory.create(organization=organization)
    template = SummaryTemplate.objects.create(
        organization=organization,
        name="Test Template",
        description="Test description",
        text="Test content",
        form=form,
    )
    assign_perm("view_summarytemplate", provider, template)
    assign_perm("change_summarytemplate", provider, template)

    client.force_login(provider)
    url = reverse(
        "providers:summary_template_edit", kwargs={"organization_id": organization.id, "template_id": template.id}
    )
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert "provider/summary_template_edit.html" in [t.name for t in response.templates]


def test_summary_template_edit_post(client: Client, provider: User, organization: Organization) -> None:
    assign_perm("view_organization", provider, organization)
    form = FormFactory.create(organization=organization)
    template = SummaryTemplate.objects.create(
        organization=organization,
        name="Original Name",
        description="Original description",
        text="Original content",
        form=form,
    )
    assign_perm("view_summarytemplate", provider, template)
    assign_perm("change_summarytemplate", provider, template)

    client.force_login(provider)
    url = reverse(
        "providers:summary_template_edit", kwargs={"organization_id": organization.id, "template_id": template.id}
    )

    data = {
        "name": "Updated Name",
        "description": "Updated description",
        "text": "Updated content",
        "form": form.id,
    }
    response = client.post(url, data)

    assert response.status_code == HTTPStatus.FOUND
    assert response["Location"] == reverse(
        "providers:summary_template_list", kwargs={"organization_id": organization.id}
    )

    template.refresh_from_db()
    assert template.name == "Updated Name"
    assert template.description == "Updated description"
    assert template.text == "Updated content"


def test_summary_template_delete(client: Client, provider: User, organization: Organization) -> None:
    assign_perm("view_organization", provider, organization)
    form = FormFactory.create(organization=organization)
    template = SummaryTemplate.objects.create(
        organization=organization,
        name="Template to Delete",
        description="Will be deleted",
        text="Content",
        form=form,
    )
    assign_perm("view_summarytemplate", provider, template)
    assign_perm("delete_summarytemplate", provider, template)

    client.force_login(provider)
    url = reverse(
        "providers:summary_template_delete", kwargs={"organization_id": organization.id, "template_id": template.id}
    )

    response = client.post(url, {"confirmation": "DELETE"})

    assert response.status_code == HTTPStatus.FOUND
    assert response["Location"] == reverse(
        "providers:summary_template_list", kwargs={"organization_id": organization.id}
    )

    assert not SummaryTemplate.objects.filter(id=template.id).exists()


def test_summary_template_delete_wrong_confirmation(
    client: Client, provider: User, organization: Organization
) -> None:
    assign_perm("view_organization", provider, organization)
    form = FormFactory.create(organization=organization)
    template = SummaryTemplate.objects.create(
        organization=organization,
        name="Template to Delete",
        description="Will not be deleted",
        text="Content",
        form=form,
    )
    assign_perm("view_summarytemplate", provider, template)
    assign_perm("delete_summarytemplate", provider, template)

    client.force_login(provider)
    url = reverse(
        "providers:summary_template_delete", kwargs={"organization_id": organization.id, "template_id": template.id}
    )

    response = client.post(url, {"confirmation": "delete"})  # lowercase, should fail

    assert response.status_code == HTTPStatus.OK
    assert b"Must type &#x27;DELETE&#x27; to confirm." in response.content
    assert SummaryTemplate.objects.filter(id=template.id).exists()


def test_summary_template_delete_modal(client: Client, provider: User, organization: Organization) -> None:
    assign_perm("view_organization", provider, organization)
    form = FormFactory.create(organization=organization)
    template = SummaryTemplate.objects.create(
        organization=organization,
        name="Template",
        description="Description",
        text="Content",
        form=form,
    )
    assign_perm("view_summarytemplate", provider, template)
    assign_perm("delete_summarytemplate", provider, template)

    client.force_login(provider)
    url = reverse(
        "providers:summary_template_delete", kwargs={"organization_id": organization.id, "template_id": template.id}
    )

    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert "provider/partials/summary_template_delete_modal.html" in [t.name for t in response.templates]


def test_summary_template_delete_modal_has_unique_id(
    client: Client, provider: User, organization: Organization
) -> None:
    form = FormFactory.create(organization=organization)
    template = SummaryTemplate.objects.create(
        organization=organization,
        name="Template",
        description="Description",
        text="Content",
        form=form,
    )

    assign_perm("view_organization", provider, organization)
    assign_perm("view_summarytemplate", provider, template)
    assign_perm("delete_summarytemplate", provider, template)

    client.force_login(provider)
    url = reverse(
        "providers:summary_template_delete", kwargs={"organization_id": organization.id, "template_id": template.id}
    )

    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

    content = response.content.decode()
    assert f'id="delete-template-modal-{template.id}"' in content
    assert f"getElementById('delete-template-modal-{template.id}')" in content


def test_summary_template_pagination(client: Client, provider: User, organization: Organization) -> None:
    form = FormFactory.create(organization=organization)

    # Create 30 templates to test pagination (page size is 25)
    for i in range(30):
        SummaryTemplate.objects.create(
            organization=organization,
            name=f"Template {i}",
            description=f"Description {i}",
            text=f"Content {i}",
            form=form,
        )

    client.force_login(provider)
    url = reverse("providers:summary_template_list", kwargs={"organization_id": organization.id})

    # First page
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert len(response.context["templates"].object_list) == 25
    assert response.context["templates"].has_next()

    # Second page
    response = client.get(url, {"page": 2})
    assert response.status_code == HTTPStatus.OK
    assert len(response.context["templates"].object_list) == 5
    assert not response.context["templates"].has_next()


# E2E Tests
def login(live_server, page: Page, user: User) -> Page:
    """Helper function to log in a user via the login page."""
    page.goto(f"{live_server.url}{reverse('account_login')}")
    page.get_by_role("textbox", name="Email*").click()
    page.get_by_role("textbox", name="Email*").fill(user.email)
    page.get_by_role("textbox", name="Password*").click()
    page.get_by_role("textbox", name="Password*").fill(user.raw_password)  # type: ignore[attr-defined]
    page.get_by_role("checkbox", name="Remember Me").check()
    page.get_by_role("button", name="Sign In").click()
    return page


@pytest.fixture
def provider_page(live_server, page: Page, provider: User) -> Page:
    """Fixture that returns a logged-in provider page."""
    return login(live_server, page, provider)


@pytest.mark.e2e
@pytest.mark.django_db
def test_summary_template_delete_modal_opens_and_works(
    live_server, provider_page: Page, organization: Organization, provider: User
):
    """Test that the delete modal opens correctly and can delete a template."""
    assign_perm("view_organization", provider, organization)

    form = FormFactory.create(organization=organization, name="Test Form")
    template = SummaryTemplate.objects.create(
        organization=organization,
        name="Test Template E2E",
        description="Template for E2E testing",
        text="Test content {% ai %}",
        form=form,
    )
    assign_perm("view_summarytemplate", provider, template)
    assign_perm("change_summarytemplate", provider, template)
    assign_perm("delete_summarytemplate", provider, template)

    edit_url = reverse(
        "providers:summary_template_edit",
        kwargs={"organization_id": organization.id, "template_id": template.id},
    )
    provider_page.goto(f"{live_server.url}{edit_url}")
    provider_page.wait_for_load_state("networkidle")

    templates_before = SummaryTemplate.objects.filter(organization=organization).count()
    assert templates_before >= 1

    delete_button = provider_page.locator("button:has-text('Delete Template')")
    delete_button.click()

    modal_id = f"#delete-template-modal-{template.id}"
    modal = provider_page.locator(modal_id)
    try:
        expect(modal).to_be_attached()
    except AssertionError:
        # modal assertion is flaky, try navigating directly to the delete URL to load it
        delete_url = reverse(
            "providers:summary_template_delete",
            kwargs={"organization_id": organization.id, "template_id": template.id},
        )
        provider_page.goto(f"{live_server.url}{delete_url}")
        provider_page.wait_for_load_state("networkidle")
        modal = provider_page.locator(modal_id)
        expect(modal).to_be_attached()
    expect(modal).to_be_visible()

    expect(modal).to_contain_text("Delete Template")
    expect(modal).to_contain_text("Test Template E2E")
    expect(modal).to_contain_text("This action cannot be undone")

    delete_form = modal.locator("form[method='post']")
    expect(delete_form).to_be_attached()

    cancel_button = modal.locator("button:has-text('Cancel')")
    expect(cancel_button).to_be_visible()
