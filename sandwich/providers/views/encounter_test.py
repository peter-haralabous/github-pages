import pytest
from django.test import Client
from django.urls import reverse

from sandwich.conftest import RoleName
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.invitation import Invitation
from sandwich.core.models.invitation import InvitationStatus
from sandwich.core.models.organization import Organization
from sandwich.core.service.invitation_service import assign_default_invitation_perms
from sandwich.core.service.organization_service import assign_organization_role
from sandwich.users.models import User


@pytest.mark.django_db
def test_encounter_details_require_authentication(
    user: User, organization: Organization, encounter: Encounter
) -> None:
    client = Client()
    url = reverse("providers:encounter", kwargs={"organization_id": organization.id, "encounter_id": encounter.id})
    result = client.get(url)

    assert result.status_code == 302
    assert "/login/" in result.url  # type: ignore[attr-defined]


@pytest.mark.django_db
def test_encounter_details_not_found_without_view_invitation_perms(
    user: User, organization: Organization, encounter: Encounter
) -> None:
    client = Client()
    client.force_login(user)
    url = reverse("providers:encounter", kwargs={"organization_id": organization.id, "encounter_id": encounter.id})
    result = client.get(url)

    assert result.status_code == 404


@pytest.mark.django_db
def test_encounter_details_returns_template(user: User, organization: Organization, encounter: Encounter) -> None:
    assign_organization_role(organization=organization, role_name=RoleName.OWNER, user=user)
    invitation = Invitation.objects.create(status=InvitationStatus.PENDING, token="", patient=encounter.patient)
    assign_default_invitation_perms(invitation)

    client = Client()
    client.force_login(user)
    url = reverse("providers:encounter", kwargs={"organization_id": organization.id, "encounter_id": encounter.id})
    result = client.get(url)

    assert result.status_code == 200
    assert "provider/encounter_details.html" in [template.name for template in result.templates]
