import pytest
from django.test import Client
from django.urls import reverse

from sandwich.core.models.organization import Organization
from sandwich.core.models.organization import VerificationType
from sandwich.core.models.role import RoleName
from sandwich.core.service.organization_service import assign_organization_role
from sandwich.providers.views.organization import OrganizationAdd
from sandwich.users.models import User


@pytest.mark.django_db
def test_organization_edit(user: User, organization: Organization) -> None:
    assign_organization_role(organization, RoleName.OWNER, user)

    client = Client()
    client.force_login(user)
    url = reverse("providers:organization_edit", kwargs={"organization_id": organization.id})
    data = {"name": "new org name", "verification_type": VerificationType.DATE_OF_BIRTH}
    res = client.post(url, data)

    assert res.status_code == 302
    organization.refresh_from_db()
    assert organization.name == "new org name"


@pytest.mark.django_db
def test_organization_edit_deny_access(user: User, organization: Organization) -> None:
    assign_organization_role(organization, RoleName.PATIENT, user)

    client = Client()
    client.force_login(user)
    url = reverse("providers:organization_edit", kwargs={"organization_id": organization.id})
    data = {"name": "new org name", "verification_type": VerificationType.DATE_OF_BIRTH}
    res = client.post(url, data)

    assert res.status_code == 404


@pytest.mark.django_db
def test_organization_delete_success(user: User, organization: Organization) -> None:
    assign_organization_role(organization=organization, role_name=RoleName.OWNER, user=user)

    client = Client()
    client.force_login(user)
    url = reverse("providers:organization_delete", kwargs={"organization_id": organization.id})
    data = {"confirmation": "DELETE"}
    result = client.post(url, data)

    assert result.status_code == 302
    assert result.url == reverse("providers:home")  # type: ignore[attr-defined]
    assert not Organization.objects.filter(id=organization.id).exists()


@pytest.mark.django_db
def test_organization_delete_deny_access(user: User, organization: Organization) -> None:
    assign_organization_role(organization=organization, role_name=RoleName.PATIENT, user=user)

    client = Client()
    client.force_login(user)
    url = reverse("providers:organization_delete", kwargs={"organization_id": organization.id})
    data = {"confirmation": "DELETE"}
    res = client.post(url, data)

    assert res.status_code == 404


@pytest.mark.django_db
def test_organization_delete_get_modal(user: User, organization: Organization) -> None:
    assign_organization_role(organization=organization, role_name=RoleName.OWNER, user=user)

    client = Client()
    client.force_login(user)
    url = reverse("providers:organization_delete", kwargs={"organization_id": organization.id})
    result = client.get(url)

    assert result.status_code == 200
    assert "provider/partials/organization_delete_modal.html" in [template.name for template in result.templates]


@pytest.mark.django_db
def test_organization_delete_invalid_form(user: User, organization: Organization) -> None:
    assign_organization_role(organization=organization, role_name=RoleName.OWNER, user=user)

    client = Client()
    client.force_login(user)
    url = reverse("providers:organization_delete", kwargs={"organization_id": organization.id})
    data = {"confirmation": "INVALID"}
    result = client.post(url, data)

    assert result.status_code == 200
    assert "provider/partials/organization_delete_modal.html" in [template.name for template in result.templates]
    assert Organization.objects.filter(id=organization.id).exists()


@pytest.mark.django_db
def test_organization_delete_unauthenticated(organization: Organization) -> None:
    client = Client()
    url = reverse("providers:organization_delete", kwargs={"organization_id": organization.id})
    result = client.post(url, {"confirmation": "DELETE"})

    assert result.status_code == 302
    assert "/login/" in result.url  # type: ignore[attr-defined]
    assert Organization.objects.filter(id=organization.id).exists()


@pytest.mark.django_db
def test_organization_add_form() -> None:
    form_data = {
        "name": "Test Organization",
    }
    form = OrganizationAdd(data=form_data)
    assert form.is_valid(), f"Form errors: {form.errors}"
    organization = form.save()
    assert organization.name == "Test Organization"


minimal_form_data = {
    "name": "Test Organization",
    "patient_statuses": "[]",
    "verification_type": "DATE_OF_BIRTH",
}


@pytest.mark.django_db
def test_organization_add_form_no_statuses() -> None:
    form = OrganizationAdd(data=minimal_form_data)
    assert form.is_valid(), f"Form errors: {form.errors}"
    organization = form.save()
    assert organization.name == "Test Organization"
    assert len(organization.patient_statuses) == 0


@pytest.mark.django_db
def test_organization_with_same_name() -> None:
    org_a = OrganizationAdd(data=minimal_form_data).save()
    org_b = OrganizationAdd(data=minimal_form_data).save()
    assert org_a.pk != org_b.pk
    assert org_a.slug != org_b.slug
