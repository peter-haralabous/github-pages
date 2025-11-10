import pytest
from django.test import Client
from django.urls import reverse
from playwright.sync_api import Page

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models import ListViewType
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.invitation import Invitation
from sandwich.core.models.invitation import InvitationStatus
from sandwich.core.models.organization import Organization
from sandwich.core.service.list_preference_service import save_list_view_preference
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


@pytest.mark.django_db
def test_encounter_list_canonicalizes_saved_filters(provider: User, organization: Organization) -> None:
    save_list_view_preference(
        organization=organization,
        list_type=ListViewType.ENCOUNTER_LIST,
        user=provider,
        visible_columns=["patient__first_name"],
        saved_filters={
            "model_fields": {"status": EncounterStatus.IN_PROGRESS.value},
            "custom_attributes": {},
        },
    )

    client = Client()
    client.force_login(provider)
    url = reverse("providers:encounter_list", kwargs={"organization_id": organization.id})
    response = client.get(url)

    assert response.status_code == 302
    assert f"filter_status={EncounterStatus.IN_PROGRESS.value}" in response["Location"]

    canonical = client.get(response["Location"])

    assert canonical.status_code == 200
    assert canonical.context is not None
    assert canonical.context["has_unsaved_filters"] is False


@pytest.mark.django_db
def test_encounter_list_shows_filter_panel_in_custom_mode_without_filters(
    provider: User,
    organization: Organization,
) -> None:
    """Filter panel should be visible with 'No Filters Applied' when filter_mode=custom and no filters set."""
    client = Client()
    client.force_login(provider)
    url = reverse("providers:encounter_list", kwargs={"organization_id": organization.id}) + "?filter_mode=custom"
    response = client.get(url)

    assert response.status_code == 200
    # Ensure main template rendered
    assert "provider/encounter_list.html" in [t.name for t in response.templates]
    content = response.content.decode()
    assert "No Filters Applied" in content
    # Save Filters button should be visible in custom mode (unsaved)
    assert "Save Filters" in content


@pytest.mark.django_db
def test_encounter_list_filters_by_is_active(provider: User, organization: Organization) -> None:
    """Test filtering encounters by is_active field."""
    patient = PatientFactory.create(organization=organization)

    active = Encounter.objects.create(organization=organization, patient=patient, status=EncounterStatus.IN_PROGRESS)
    inactive = Encounter.objects.create(organization=organization, patient=patient, status=EncounterStatus.COMPLETED)

    client = Client()
    client.force_login(provider)
    url = reverse("providers:encounter_list", kwargs={"organization_id": organization.id})

    # Test filter for active encounters
    response = client.get(f"{url}?filter_is_active=True")
    assert response.status_code == 200
    encounters = list(response.context["encounters"])
    assert active in encounters
    assert inactive not in encounters

    # Test filter for inactive encounters
    response = client.get(f"{url}?filter_is_active=False")
    assert response.status_code == 200
    encounters = list(response.context["encounters"])
    assert inactive in encounters
    assert active not in encounters


@pytest.mark.django_db
def test_encounter_list_sorts_by_is_active(provider: User, organization: Organization) -> None:
    """Test sorting encounters by is_active field."""
    patient = PatientFactory.create(organization=organization)

    active = Encounter.objects.create(organization=organization, patient=patient, status=EncounterStatus.IN_PROGRESS)
    inactive = Encounter.objects.create(organization=organization, patient=patient, status=EncounterStatus.COMPLETED)

    client = Client()
    client.force_login(provider)
    url = reverse("providers:encounter_list", kwargs={"organization_id": organization.id})

    # Test ascending sort
    response = client.get(f"{url}?sort=is_active")
    assert response.status_code == 200
    encounters = list(response.context["encounters"])
    assert encounters[0] == inactive
    assert encounters[1] == active

    # Test descending sort
    response = client.get(f"{url}?sort=-is_active")
    assert response.status_code == 200
    encounters = list(response.context["encounters"])
    assert encounters[0] == active
    assert encounters[1] == inactive


@pytest.mark.e2e
@pytest.mark.django_db
def test_encounter_slideout_closes_when_clicking_outside(  # noqa: PLR0913
    live_server, page: Page, provider: User, organization: Organization, encounter: Encounter, auth_cookies
) -> None:
    """Test that clicking outside the slideout closes it."""
    url = f"{live_server.url}{reverse('providers:encounter_list', kwargs={'organization_id': organization.id})}"
    page.goto(url)
    page.wait_for_load_state("networkidle")

    first_patient_link = page.locator('label[for^="encounter-details-modal-"]').first
    first_patient_link.click()

    for_attr = first_patient_link.get_attribute("for")
    assert for_attr is not None, "Label should have a 'for' attribute"
    encounter_id = for_attr.replace("encounter-details-modal-", "")

    slideout = page.locator(f"#encounter-details-modal-{encounter_id}")
    page.wait_for_timeout(300)
    assert slideout.is_checked()

    # Click outside (on the backdrop) to close
    backdrop = page.locator(f'label[for="encounter-details-modal-{encounter_id}"]').first
    backdrop.click(force=True)

    page.wait_for_timeout(300)

    assert not slideout.is_checked()
