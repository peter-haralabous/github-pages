import pytest
from django.test import Client
from django.urls import reverse
from playwright.sync_api import Page

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.invitation import Invitation
from sandwich.core.models.invitation import InvitationStatus
from sandwich.core.models.organization import Organization
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
def test_encounter_details_not_found_without_view_encounter_perms(user: User, organization: Organization) -> None:
    client = Client()
    client.force_login(user)

    random_patient = PatientFactory.create()
    # User is not related to this encounter
    encounter = Encounter.objects.create(
        status=EncounterStatus.IN_PROGRESS, patient=random_patient, organization=organization
    )

    url = reverse("providers:encounter", kwargs={"organization_id": organization.id, "encounter_id": encounter.id})
    result = client.get(url)

    assert result.status_code == 404


@pytest.mark.django_db
def test_encounter_details_returns_template(provider: User, organization: Organization, encounter: Encounter) -> None:
    Invitation.objects.create(status=InvitationStatus.PENDING, token="", patient=encounter.patient)

    client = Client()
    client.force_login(provider)
    url = reverse("providers:encounter", kwargs={"organization_id": organization.id, "encounter_id": encounter.id})
    result = client.get(url)

    assert result.status_code == 200
    assert "provider/encounter_details.html" in [template.name for template in result.templates]


@pytest.mark.e2e
@pytest.mark.django_db
def test_encounter_slideout_closes_when_clicking_outside(
    live_server, page: Page, provider: User, organization: Organization, encounter: Encounter
) -> None:
    """Test that clicking outside the slideout closes it."""
    url = f"{live_server.url}{reverse('providers:encounter_list', kwargs={'organization_id': organization.id})}"
    page.goto(url)

    page.get_by_role("row").filter(has_text=encounter.patient.last_name).click()

    slideout = page.locator(f"#encounter-details-modal-{encounter.id}")
    assert slideout.is_checked()

    # Click outside (on the backdrop)
    page.locator(f'label[for="encounter-details-modal-{encounter.id}"]').first.click()

    assert not slideout.is_checked()
