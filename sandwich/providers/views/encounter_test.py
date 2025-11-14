from datetime import date
from urllib.parse import urlparse

import pytest
from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY
from django.contrib.auth import HASH_SESSION_KEY
from django.contrib.auth import SESSION_KEY
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.backends.db import SessionStore
from django.test import Client
from django.urls import reverse
from playwright.sync_api import Page

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models import ListViewType
from sandwich.core.models.custom_attribute import CustomAttribute
from sandwich.core.models.custom_attribute import CustomAttributeEnum
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
def test_encounter_details_includes_custom_attributes(
    provider: User, organization: Organization, encounter: Encounter
) -> None:
    """Test that custom attributes are included in the encounter details context."""

    # Create custom attributes for encounters
    content_type = ContentType.objects.get_for_model(Encounter)

    date_attr = CustomAttribute.objects.create(
        organization=organization,
        content_type=content_type,
        name="Follow-up Date",
        data_type=CustomAttribute.DataType.DATE,
    )

    enum_attr = CustomAttribute.objects.create(
        organization=organization,
        content_type=content_type,
        name="Priority",
        data_type=CustomAttribute.DataType.ENUM,
    )

    high_priority = CustomAttributeEnum.objects.create(
        attribute=enum_attr,
        label="High",
        value="high",
    )

    # Add values to the encounter
    encounter.attributes.create(attribute=date_attr, value_date=date(2025, 12, 31))
    encounter.attributes.create(attribute=enum_attr, value_enum=high_priority)

    client = Client()
    client.force_login(provider)
    url = reverse("providers:encounter", kwargs={"organization_id": organization.id, "encounter_id": encounter.id})
    result = client.get(url)

    assert result.status_code == 200
    assert result.context is not None
    assert "formatted_attributes" in result.context

    formatted_attrs = result.context["formatted_attributes"]
    assert len(formatted_attrs) == 2

    # Check that both attributes are present with correct values
    attr_dict = {attr["name"]: attr["value"] for attr in formatted_attrs}
    assert attr_dict["Follow-up Date"] == "2025-12-31"
    assert attr_dict["Priority"] == "High"


@pytest.mark.django_db
def test_encounter_details_shows_custom_attributes_with_no_value(
    provider: User, organization: Organization, encounter: Encounter
) -> None:
    """Test that custom attributes without values show None in context."""

    # Create a custom attribute but don't set a value
    content_type = ContentType.objects.get_for_model(Encounter)
    CustomAttribute.objects.create(
        organization=organization,
        content_type=content_type,
        name="Notes",
        data_type=CustomAttribute.DataType.DATE,
    )

    client = Client()
    client.force_login(provider)
    url = reverse("providers:encounter", kwargs={"organization_id": organization.id, "encounter_id": encounter.id})
    result = client.get(url)

    assert result.status_code == 200
    assert result.context is not None
    formatted_attrs = result.context["formatted_attributes"]

    # Find the Notes attribute
    notes_attr = next((a for a in formatted_attrs if a["name"] == "Notes"), None)
    assert notes_attr is not None
    assert notes_attr["value"] is None


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

    response = client.get(f"{url}?sort=is_active")
    assert response.status_code == 200
    encounters = list(response.context["encounters"])
    assert encounters[0] == inactive
    assert encounters[1] == active

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


@pytest.mark.e2e
@pytest.mark.django_db
def test_inline_edit_status_field_updates_display(
    live_server, page: Page, provider: User, organization: Organization, encounter: Encounter
) -> None:
    """Test that inline editing a status field updates the display value."""
    encounter.status = EncounterStatus.IN_PROGRESS
    encounter.save()

    # Create auth cookies for the provider (not the basic user)
    session = SessionStore()
    session[SESSION_KEY] = str(provider.pk)
    session[BACKEND_SESSION_KEY] = "django.contrib.auth.backends.ModelBackend"
    session[HASH_SESSION_KEY] = provider.get_session_auth_hash()
    session.save()

    parsed = urlparse(live_server.url)
    domain = parsed.hostname or "localhost"

    session_key = session.session_key
    assert session_key is not None, "Session key should not be None"

    page.context.add_cookies(
        [
            {
                "name": settings.SESSION_COOKIE_NAME,
                "value": session_key,
                "domain": domain,
                "path": "/",
                "httpOnly": True,
            }
        ]
    )

    url = f"{live_server.url}{reverse('providers:encounter_list', kwargs={'organization_id': organization.id})}"
    page.goto(url)
    page.wait_for_load_state("networkidle")

    # First, verify there's at least one encounter in the table
    table = page.locator("table")
    assert table.is_visible(), "Encounter table should be visible"

    # Look for any status cell (may need to find it differently if column order varies)
    # Try to find the patient name link first
    patient_link = page.locator(f"text=/{encounter.patient.last_name}, {encounter.patient.first_name}/i").first
    if not patient_link.is_visible():
        msg = f"Patient {encounter.patient.first_name} {encounter.patient.last_name} not found in table"
        raise AssertionError(msg)

    row = patient_link.locator("xpath=ancestor::tr")

    # Find the status cell within this row
    status_cell = (
        row.locator("td").filter(has_text="In Progress").or_(row.locator("td").filter(has_text="IN_PROGRESS"))
    )

    status_cell.wait_for(state="visible", timeout=5000)

    status_cell.click()

    # Wait for HTMX to swap the cell content with the form
    page.wait_for_timeout(500)

    # Wait for the form to appear in the row (the cell was replaced by HTMX)
    select = row.locator("select[name='value']")
    select.wait_for(state="visible", timeout=5000)

    select.select_option(EncounterStatus.COMPLETED.value)

    # Wait for HTMX to process the form submission and the display to update
    # The select should disappear after submission
    select.wait_for(state="hidden", timeout=3000)

    # Verify the display was updated - look in the same row again
    updated_cell = row.locator("td").filter(has_text="Completed").or_(row.locator("td").filter(has_text="COMPLETED"))
    assert updated_cell.is_visible(), "Status cell should show 'Completed' after update"

    encounter.refresh_from_db()
    assert encounter.status == EncounterStatus.COMPLETED


@pytest.mark.e2e
@pytest.mark.django_db
def test_inline_edit_can_be_cancelled_with_escape(
    live_server, page: Page, provider: User, organization: Organization, encounter: Encounter
) -> None:
    """Test that pressing Escape cancels inline editing without saving."""
    encounter.status = EncounterStatus.IN_PROGRESS
    encounter.save()

    # Create auth cookies for the provider
    session = SessionStore()
    session[SESSION_KEY] = str(provider.pk)
    session[BACKEND_SESSION_KEY] = "django.contrib.auth.backends.ModelBackend"
    session[HASH_SESSION_KEY] = provider.get_session_auth_hash()
    session.save()

    parsed = urlparse(live_server.url)
    domain = parsed.hostname or "localhost"

    session_key = session.session_key
    assert session_key is not None, "Session key should not be None"

    page.context.add_cookies(
        [
            {
                "name": settings.SESSION_COOKIE_NAME,
                "value": session_key,
                "domain": domain,
                "path": "/",
                "httpOnly": True,
            }
        ]
    )

    url = f"{live_server.url}{reverse('providers:encounter_list', kwargs={'organization_id': organization.id})}"
    page.goto(url)
    page.wait_for_load_state("networkidle")

    table = page.locator("table")
    assert table.is_visible(), "Encounter table should be visible"

    patient_link = table.locator(f"text=/{encounter.patient.last_name}, {encounter.patient.first_name}/i").first
    if not patient_link.is_visible():
        msg = f"Patient {encounter.patient.first_name} {encounter.patient.last_name} not found in table"
        raise AssertionError(msg)

    row = patient_link.locator("xpath=ancestor::tr")

    status_cell = (
        row.locator("td").filter(has_text="In Progress").or_(row.locator("td").filter(has_text="IN_PROGRESS"))
    ).first

    status_cell.wait_for(state="visible", timeout=5000)

    status_cell.click()

    # Wait for HTMX to swap the cell content with the form
    page.wait_for_timeout(500)

    # Wait for the form to appear in the row (the cell was replaced by HTMX)
    select = row.locator("select[name='value']")
    select.wait_for(state="visible", timeout=5000)

    select.press("Escape")

    select.wait_for(state="hidden", timeout=3000)

    # Verify the display is back to original value
    cancelled_cell = (
        row.locator("td").filter(has_text="In Progress").or_(row.locator("td").filter(has_text="IN_PROGRESS"))
    ).first
    assert cancelled_cell.is_visible(), "Status cell should show 'In Progress' after cancelling"
    cancelled_text = cancelled_cell.text_content()
    assert cancelled_text is not None
    assert "In Progress" in cancelled_text or "IN_PROGRESS" in cancelled_text

    encounter.refresh_from_db()
    assert encounter.status == EncounterStatus.IN_PROGRESS


@pytest.mark.e2e
@pytest.mark.django_db
def test_inline_edit_custom_enum_updates_display(
    live_server, page: Page, provider: User, organization: Organization, encounter: Encounter
) -> None:
    """Test that inline editing a custom enum attribute updates the display with the correct label."""
    # Create a custom enum attribute
    content_type = ContentType.objects.get_for_model(Encounter)
    priority_attr = CustomAttribute.objects.create(
        organization=organization,
        name="Priority",
        data_type=CustomAttribute.DataType.ENUM,
        content_type=content_type,
    )
    low_priority = CustomAttributeEnum.objects.create(
        attribute=priority_attr,
        label="Low",
        value="low",
        color_code="00FF00",
    )
    high_priority = CustomAttributeEnum.objects.create(
        attribute=priority_attr,
        label="High",
        value="high",
        color_code="FF0000",
    )

    # Set initial value to Low
    encounter.attributes.create(attribute=priority_attr, value_enum=low_priority)

    # Save list preference to show the custom attribute column
    save_list_view_preference(
        organization=organization,
        list_type=ListViewType.ENCOUNTER_LIST,
        user=provider,
        visible_columns=["patient__first_name", "patient__last_name", "status", str(priority_attr.id)],
        saved_filters={},
    )

    # Create auth cookies for the provider
    session = SessionStore()
    session[SESSION_KEY] = str(provider.pk)
    session[BACKEND_SESSION_KEY] = "django.contrib.auth.backends.ModelBackend"
    session[HASH_SESSION_KEY] = provider.get_session_auth_hash()
    session.save()

    parsed = urlparse(live_server.url)
    domain = parsed.hostname or "localhost"

    session_key = session.session_key
    assert session_key is not None, "Session key should not be None"

    page.context.add_cookies(
        [
            {
                "name": settings.SESSION_COOKIE_NAME,
                "value": session_key,
                "domain": domain,
                "path": "/",
                "httpOnly": True,
            }
        ]
    )

    url = f"{live_server.url}{reverse('providers:encounter_list', kwargs={'organization_id': organization.id})}"
    page.goto(url)
    page.wait_for_load_state("networkidle")

    table = page.locator("table")
    assert table.is_visible(), "Encounter table should be visible"

    patient_link = page.locator(f"text=/{encounter.patient.last_name}, {encounter.patient.first_name}/i").first
    if not patient_link.is_visible():
        msg = f"Patient {encounter.patient.first_name} {encounter.patient.last_name} not found in table"
        raise AssertionError(msg)

    row = patient_link.locator("xpath=ancestor::tr")

    priority_cell = row.locator("td").filter(has_text="Low").first

    priority_cell.wait_for(state="visible", timeout=5000)
    initial_text = priority_cell.text_content()
    assert initial_text is not None
    assert "Low" in initial_text, f"Expected 'Low' in cell but got: {initial_text}"

    priority_cell.click()

    # Wait for HTMX to swap the cell content with the form
    page.wait_for_timeout(500)

    # Wait for the form to appear in the row (the cell was replaced by HTMX)
    select = row.locator("select[name='value']")
    select.wait_for(state="visible", timeout=5000)

    select.select_option(str(high_priority.id))

    # Wait for HTMX to process the form submission and the display to update
    # The select should disappear after submission
    select.wait_for(state="hidden", timeout=3000)

    # Verify the display was updated to show "High" (the label, not "high" the value)
    updated_cell = row.locator("td").filter(has_text="High").first
    updated_cell.wait_for(state="visible", timeout=2000)
    updated_text = updated_cell.text_content()
    assert updated_text is not None
    assert "High" in updated_text, f"Expected 'High' in cell after update but got: {updated_text}"
    assert "high" not in updated_text or "High" in updated_text, "Should show label 'High', not value 'high'"

    encounter.refresh_from_db()
    attr_value = encounter.attributes.get(attribute=priority_attr)
    assert attr_value.value_enum == high_priority
