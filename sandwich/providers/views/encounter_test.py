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
from playwright.sync_api import expect

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.factories.summary import SummaryFactory
from sandwich.core.factories.task import TaskFactory
from sandwich.core.models import ListViewType
from sandwich.core.models.custom_attribute import CustomAttribute
from sandwich.core.models.custom_attribute import CustomAttributeEnum
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.invitation import Invitation
from sandwich.core.models.invitation import InvitationStatus
from sandwich.core.models.organization import Organization
from sandwich.core.service.list_preference_service import save_list_view_preference
from sandwich.core.types import EMPTY_VALUE_DISPLAY
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
    assert "enriched_attributes" in result.context

    enriched_attrs = result.context["enriched_attributes"]
    assert len(enriched_attrs) == 2

    # Check that both attributes are present with correct values
    attr_dict = {attr["name"]: attr["value"] for attr in enriched_attrs}
    assert attr_dict["Follow-up Date"] == "2025-12-31"
    assert attr_dict["Priority"] == "High"


@pytest.mark.django_db
def test_encounter_details_shows_custom_attributes_with_no_value(
    provider: User, organization: Organization, encounter: Encounter
) -> None:
    """Test that custom attributes without values show EMPTY_VALUE_DISPLAY in context."""

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
    enriched_attrs = result.context["enriched_attributes"]

    # Find the Notes attribute
    notes_attr = next((a for a in enriched_attrs if a["name"] == "Notes"), None)
    assert notes_attr is not None
    assert notes_attr["value"] == EMPTY_VALUE_DISPLAY


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
def test_encounter_list_default_excludes_archived_encounters(provider: User, organization: Organization) -> None:
    """Test that archived encounters are excluded by default on first load."""
    patient = PatientFactory.create(organization=organization)

    active = Encounter.objects.create(organization=organization, patient=patient, status=EncounterStatus.IN_PROGRESS)
    archived = Encounter.objects.create(organization=organization, patient=patient, status=EncounterStatus.COMPLETED)

    client = Client()
    client.force_login(provider)
    url = reverse("providers:encounter_list", kwargs={"organization_id": organization.id})

    # First load without any query parameters should exclude archived encounters
    response = client.get(url, follow=True)
    assert response.status_code == 200
    encounters = list(response.context["encounters"])
    assert active in encounters
    assert archived not in encounters


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

    # Use filter_mode=custom to bypass default filter and see all encounters
    response = client.get(f"{url}?sort=is_active&filter_mode=custom", follow=True)
    assert response.status_code == 200
    encounters = list(response.context["encounters"])
    # Ascending sort: inactive (False) comes before active (True)
    assert encounters[0] == inactive
    assert encounters[1] == active

    response = client.get(f"{url}?sort=-is_active&filter_mode=custom", follow=True)
    assert response.status_code == 200
    encounters = list(response.context["encounters"])
    # Descending sort: active (True) comes before inactive (False)
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

    patient_anchor = page.locator(
        f"a.link:has-text('{encounter.patient.last_name}, {encounter.patient.first_name}')"
    ).first
    patient_anchor.wait_for(state="visible", timeout=5000)
    patient_anchor.click()

    slideout = page.locator("[id^='encounter-details-modal-']").first
    slideout.wait_for(state="attached", timeout=5000)
    backdrop = page.locator("[id^='encounter-details-backdrop-']").first
    backdrop.wait_for(state="attached", timeout=5000)

    modal_id = slideout.get_attribute("id")
    assert modal_id is not None, "Modal id missing"
    assert modal_id.startswith("encounter-details-modal-"), f"Unexpected modal id: {modal_id}"
    encounter_id = modal_id.replace("encounter-details-modal-", "")

    page.wait_for_timeout(500)

    assert backdrop.evaluate("el => el.classList.contains('opacity-100')"), "Backdrop should be visible"
    assert backdrop.evaluate("el => el.classList.contains('pointer-events-auto')"), "Backdrop should be clickable"
    assert not slideout.evaluate("el => el.classList.contains('translate-x-full')"), "Slideout should be visible"

    backdrop.click(position={"x": 10, "y": 10})

    page.wait_for_function(
        f"document.querySelector('#encounter-details-backdrop-{encounter_id}').classList.contains('opacity-0')"
    )
    page.wait_for_function(
        f"document.querySelector('#encounter-details-backdrop-{encounter_id}').classList.contains('pointer-events-none')"
    )
    page.wait_for_function(
        f"document.querySelector('#encounter-details-modal-{encounter_id}').classList.contains('translate-x-full')"
    )

    assert backdrop.evaluate("el => el.classList.contains('opacity-0')"), "Backdrop should be hidden"
    assert backdrop.evaluate("el => el.classList.contains('pointer-events-none')"), "Backdrop should not be clickable"
    assert slideout.evaluate("el => el.classList.contains('translate-x-full')"), "Slideout should be hidden"


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

    # Wait for the Choices.js dropdown to appear within the inline-edit-field
    inline_edit = row.locator("inline-edit-field")
    inline_edit.wait_for(state="attached", timeout=3000)

    choices_container = inline_edit.locator(".choices")
    choices_container.wait_for(state="visible", timeout=5000)

    dropdown_item = choices_container.locator(".choices__item--choice", has_text="Completed")
    dropdown_item.wait_for(state="visible", timeout=2000)
    dropdown_item.click()

    # Wait for HTMX to process the form submission and the display to update
    choices_container.wait_for(state="hidden", timeout=3000)

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

    # Wait for the Choices.js dropdown to appear within the inline-edit-field
    inline_edit = row.locator("inline-edit-field")
    inline_edit.wait_for(state="attached", timeout=3000)

    choices_container = inline_edit.locator(".choices")
    choices_container.wait_for(state="visible", timeout=5000)

    # Press Escape on the Choices container to cancel
    choices_container.press("Escape")

    # After pressing Escape, the entire cell should be swapped back to display mode by HTMX
    # Wait for the choices container to be hidden/removed as the cell reverts to display mode
    page.wait_for_timeout(500)

    # Verify the display is back to original value - find it in the row again
    cancelled_cell = (
        row.locator("td").filter(has_text="In Progress").or_(row.locator("td").filter(has_text="IN_PROGRESS"))
    ).first
    cancelled_cell.wait_for(state="visible", timeout=2000)
    assert cancelled_cell.is_visible(), "Status cell should show 'In Progress' after cancelling"

    encounter.refresh_from_db()
    assert encounter.status == EncounterStatus.IN_PROGRESS


@pytest.mark.e2e
@pytest.mark.django_db
def test_inline_edit_custom_enum_updates_display(  # noqa: PLR0915
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

    # Wait for the Choices.js dropdown to appear within the inline-edit-field
    inline_edit = row.locator("inline-edit-field")
    inline_edit.wait_for(state="attached", timeout=3000)

    choices_container = inline_edit.locator(".choices")
    choices_container.wait_for(state="visible", timeout=5000)

    # Click on the dropdown option for High priority
    # Choices.js shows options as items in a dropdown list
    dropdown_item = choices_container.locator(".choices__item--choice", has_text="High")
    dropdown_item.wait_for(state="visible", timeout=2000)
    dropdown_item.click()

    choices_container.wait_for(state="hidden", timeout=3000)
    # Wait for HTMX to process the form submission and the display to update
    # The choices container should disappear after submission
    choices_container.wait_for(state="hidden", timeout=3000)

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


@pytest.mark.django_db
def test_encounter_archive_changes_in_progress_to_completed(
    provider: User, organization: Organization, encounter: Encounter
) -> None:
    encounter.status = EncounterStatus.IN_PROGRESS
    encounter.save()

    client = Client()
    client.force_login(provider)
    url = reverse(
        "providers:encounter_archive", kwargs={"organization_id": organization.id, "encounter_id": encounter.id}
    )
    result = client.post(url, follow=True)

    assert result.status_code == 200
    encounter.refresh_from_db()
    assert encounter.status == EncounterStatus.COMPLETED

    messages = list(result.context["messages"])
    assert len(messages) == 1
    assert "archived successfully" in str(messages[0]).lower()


@pytest.mark.django_db
def test_encounter_archive_changes_completed_to_in_progress(
    provider: User, organization: Organization, encounter: Encounter
) -> None:
    encounter.status = EncounterStatus.COMPLETED
    encounter.save()

    client = Client()
    client.force_login(provider)
    url = reverse(
        "providers:encounter_archive", kwargs={"organization_id": organization.id, "encounter_id": encounter.id}
    )
    result = client.post(url, follow=True)

    assert result.status_code == 200
    encounter.refresh_from_db()
    assert encounter.status == EncounterStatus.IN_PROGRESS

    messages = list(result.context["messages"])
    assert len(messages) == 1
    assert "unarchived successfully" in str(messages[0]).lower()


@pytest.mark.e2e
@pytest.mark.django_db
def test_kebab_menu_visible_in_table(
    live_server, page: Page, provider: User, organization: Organization, encounter: Encounter
) -> None:
    """Test that kebab menu dropdowns are visible and not clipped."""
    session = SessionStore()
    session[SESSION_KEY] = str(provider.pk)
    session[BACKEND_SESSION_KEY] = "django.contrib.auth.backends.ModelBackend"
    session[HASH_SESSION_KEY] = provider.get_session_auth_hash()
    session.save()

    session_key = session.session_key
    assert session_key is not None, "Session key should not be None"

    page.context.add_cookies(
        [
            {
                "name": settings.SESSION_COOKIE_NAME,
                "value": session_key,
                "domain": urlparse(live_server.url).hostname or "localhost",
                "path": "/",
                "httpOnly": True,
            }
        ]
    )

    page.goto(f"{live_server.url}{reverse('providers:encounter_list', kwargs={'organization_id': organization.id})}")
    page.wait_for_load_state("networkidle")

    page.locator('button[aria-label="Encounter actions menu"]').first.click()

    dropdown = page.locator("table .dropdown-content.menu").first
    patient_details = dropdown.locator("text=Patient Details")
    encounter_details = dropdown.locator("text=Encounter Details")
    expect(patient_details).to_be_visible()
    expect(encounter_details).to_be_visible()


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
def test_inline_edit_custom_attribute_on_encounter_details_page(
    live_server, page: Page, provider: User, organization: Organization, encounter: Encounter
) -> None:
    """Test that inline editing custom attributes works on the full encounter details page."""
    # Create a custom attribute for encounters
    content_type = ContentType.objects.get_for_model(Encounter)
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

    low_priority = CustomAttributeEnum.objects.create(
        attribute=enum_attr,
        label="Low",
        value="low",
    )

    # Set initial value
    encounter.attributes.create(
        attribute=enum_attr,
        value_enum=low_priority,
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

    # Navigate to encounter details page
    url = f"{live_server.url}" + reverse(
        "providers:encounter",
        kwargs={
            "organization_id": organization.id,
            "encounter_id": encounter.id,
        },
    )
    page.goto(url)
    page.wait_for_load_state("networkidle")

    # Wait for the Encounter Details section to be visible
    expect(page.locator('h3:has-text("Encounter Details")')).to_be_visible(timeout=10000)

    # Check that the Priority attribute is visible on the page
    expect(page.locator("text=Priority")).to_be_visible()

    # Find the specific tr element containing the Priority label
    priority_container = page.locator('tr.flex.flex-col.gap-y-1:has(th.text-sm:text("Priority"))')
    expect(priority_container).to_be_visible()

    # Find the inline edit cell in that container showing "Low"
    priority_cell = priority_container.locator("td.inline-edit-cell")
    expect(priority_cell).to_contain_text("Low")

    # Click to enter edit mode
    priority_cell.click()

    # Wait for HTMX to swap the cell content with the form
    page.wait_for_timeout(500)

    # Wait for the Choices.js dropdown to appear within the inline-edit-field
    inline_edit = priority_container.locator("inline-edit-field")
    inline_edit.wait_for(state="attached", timeout=3000)

    choices_container = inline_edit.locator(".choices")
    choices_container.wait_for(state="visible", timeout=5000)

    # Click on the dropdown option for High priority
    dropdown_item = choices_container.locator(".choices__item--choice", has_text="High")
    dropdown_item.wait_for(state="visible", timeout=2000)
    dropdown_item.click()

    # Wait for HTMX to process the form submission and update the display
    choices_container.wait_for(state="hidden", timeout=3000)

    # Verify the display was updated to show "High"
    page.wait_for_timeout(1000)  # Give time for the swap to complete
    expect(priority_container.locator("td.inline-edit-cell")).to_contain_text("High")

    # Verify the database was updated
    encounter.refresh_from_db()
    value = encounter.attributes.filter(attribute=enum_attr).first()
    assert value is not None
    assert value.value_enum == high_priority


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
def test_inline_edit_custom_attribute_in_encounter_slideout(  # noqa: PLR0915
    live_server, page: Page, provider: User, organization: Organization, encounter: Encounter
) -> None:
    """Test that inline editing custom attributes works in the encounter details slideout."""
    # Create a custom attribute for encounters
    content_type = ContentType.objects.get_for_model(Encounter)
    enum_attr = CustomAttribute.objects.create(
        organization=organization,
        content_type=content_type,
        name="Urgency",
        data_type=CustomAttribute.DataType.ENUM,
    )

    urgent = CustomAttributeEnum.objects.create(
        attribute=enum_attr,
        label="Urgent",
        value="urgent",
    )

    routine = CustomAttributeEnum.objects.create(
        attribute=enum_attr,
        label="Routine",
        value="routine",
    )

    # Set initial value
    encounter.attributes.create(
        attribute=enum_attr,
        value_enum=routine,
    )

    # Save list preference to show the custom attribute column in the table
    save_list_view_preference(
        organization=organization,
        list_type=ListViewType.ENCOUNTER_LIST,
        user=provider,
        visible_columns=["patient__first_name", "status", str(enum_attr.id)],
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

    # Navigate to encounter list
    url = f"{live_server.url}{reverse('providers:encounter_list', kwargs={'organization_id': organization.id})}"
    page.goto(url)
    page.wait_for_load_state("networkidle")

    # Find and click on the patient name to open the slideout
    patient_name = f"{encounter.patient.last_name}, {encounter.patient.first_name}"
    patient_link = page.locator(f'a.link:has-text("{patient_name}")').first
    patient_link.click()

    # Wait for slideout to appear and content to load
    slideout = page.locator(f"#encounter-details-modal-{encounter.id}")
    expect(slideout).to_be_visible(timeout=10000)

    # Wait for the Encounter Details heading to ensure content is loaded
    expect(slideout.locator('h3:has-text("Encounter Details")')).to_be_visible(timeout=5000)

    # Find the specific tr element containing the Urgency label within the slideout
    urgency_container = slideout.locator('tr.flex.flex-col.gap-y-1:has(th.text-sm:text("Urgency"))')
    expect(urgency_container).to_be_visible(timeout=5000)

    # Find the inline edit cell in that container showing "Routine"
    urgency_cell = urgency_container.locator("td.inline-edit-cell")
    expect(urgency_cell).to_contain_text("Routine")

    # Click to enter edit mode
    urgency_cell.click()

    # Wait for HTMX to swap the cell content with the form
    page.wait_for_timeout(500)

    # Wait for the Choices.js dropdown to appear within the inline-edit-field
    inline_edit = urgency_container.locator("inline-edit-field")
    inline_edit.wait_for(state="attached", timeout=3000)

    choices_container = inline_edit.locator(".choices")
    choices_container.wait_for(state="visible", timeout=5000)

    # Click on the dropdown option for Urgent
    dropdown_item = choices_container.locator(".choices__item--choice", has_text="Urgent")
    dropdown_item.wait_for(state="visible", timeout=2000)
    dropdown_item.click()

    # Wait for HTMX to process the form submission and update the display
    choices_container.wait_for(state="hidden", timeout=3000)

    # Verify the display was updated to show "Urgent"
    page.wait_for_timeout(1000)  # Give time for the swap to complete
    expect(urgency_container.locator("td.inline-edit-cell")).to_contain_text("Urgent")

    # Verify the database was updated
    encounter.refresh_from_db()
    value = encounter.attributes.filter(attribute=enum_attr).first()
    assert value is not None
    assert value.value_enum == urgent

    # Close the slideout by clicking the backdrop
    backdrop = page.locator(f"#encounter-details-backdrop-{encounter.id}")
    backdrop.click(position={"x": 10, "y": 10})

    # Wait for slideout to close
    page.wait_for_function(
        f"document.querySelector('#encounter-details-modal-{encounter.id}').classList.contains('translate-x-full')"
    )
    page.wait_for_timeout(500)

    # Verify the table row was updated via OOB swap
    # Find the encounter row in the table and check the Urgency column shows "Urgent"
    patient_link_in_table = page.locator(f'a.link:has-text("{patient_name}")').first
    encounter_row = patient_link_in_table.locator("xpath=ancestor::tr")
    table_urgency_cell = encounter_row.locator("td.inline-edit-cell").filter(has_text="Urgent")
    expect(table_urgency_cell).to_be_visible(timeout=2000)
    expect(table_urgency_cell).to_contain_text("Urgent")


@pytest.mark.django_db
def test_encounter_details_summaries_pagination(provider: User, organization: Organization, encounter: Encounter):
    """Test that summaries are paginated correctly."""
    # Create 15 summaries to trigger pagination (5 per page)
    for i in range(15):
        SummaryFactory.create(
            patient=encounter.patient, organization=organization, encounter=encounter, title=f"Summary {i}"
        )

    client = Client()
    client.force_login(provider)
    url = reverse("providers:encounter", kwargs={"organization_id": organization.id, "encounter_id": encounter.id})

    # Test first page
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.context["summaries"]) == 5
    assert response.context["summaries"].number == 1
    assert response.context["summaries"].paginator.num_pages == 3

    # Test second page
    response = client.get(url + "?summaries_page=2")
    assert response.status_code == 200
    assert len(response.context["summaries"]) == 5
    assert response.context["summaries"].number == 2

    # Test third page
    response = client.get(url + "?summaries_page=3")
    assert response.status_code == 200
    assert len(response.context["summaries"]) == 5
    assert response.context["summaries"].number == 3


@pytest.mark.django_db
def test_encounter_details_summaries_htmx_pagination(provider: User, organization: Organization, encounter: Encounter):
    """Test that HTMX requests for summaries return only the section template."""
    # Create 15 summaries
    for _i in range(15):
        SummaryFactory.create(patient=encounter.patient, organization=organization, encounter=encounter)

    client = Client()
    client.force_login(provider)
    url = reverse("providers:encounter", kwargs={"organization_id": organization.id, "encounter_id": encounter.id})

    # Test HTMX request for summaries section
    response = client.get(url + "?section=summaries&summaries_page=2", HTTP_HX_REQUEST="true")
    assert response.status_code == 200
    assert "provider/partials/summaries_section.html" in [template.name for template in response.templates]
    assert response.context["summaries"].number == 2


@pytest.mark.django_db
def test_encounter_details_forms_pagination(provider: User, organization: Organization, encounter: Encounter):
    """Test that forms (tasks + documents combined) are paginated correctly."""
    # Create 15 tasks to trigger pagination
    for _i in range(15):
        TaskFactory.create(patient=encounter.patient, encounter=encounter)

    client = Client()
    client.force_login(provider)
    url = reverse("providers:encounter", kwargs={"organization_id": organization.id, "encounter_id": encounter.id})

    # Test first page
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.context["tasks_and_documents"]) == 5
    assert response.context["tasks_and_documents"].number == 1
    assert response.context["tasks_and_documents"].paginator.num_pages == 3

    # Test second page
    response = client.get(url + "?forms_page=2")
    assert response.status_code == 200
    assert len(response.context["tasks_and_documents"]) == 5
    assert response.context["tasks_and_documents"].number == 2

    # Test third page
    response = client.get(url + "?forms_page=3")
    assert response.status_code == 200
    assert len(response.context["tasks_and_documents"]) == 5
    assert response.context["tasks_and_documents"].number == 3


@pytest.mark.django_db
def test_encounter_details_forms_htmx_pagination(provider: User, organization: Organization, encounter: Encounter):
    """Test that HTMX requests for forms return only the section template."""
    # Create 15 tasks
    for _i in range(15):
        TaskFactory.create(patient=encounter.patient, encounter=encounter)

    client = Client()
    client.force_login(provider)
    url = reverse("providers:encounter", kwargs={"organization_id": organization.id, "encounter_id": encounter.id})

    # Test HTMX request for forms section
    response = client.get(url + "?section=forms&forms_page=2", HTTP_HX_REQUEST="true")
    assert response.status_code == 200
    assert "provider/partials/documents_and_forms_section.html" in [template.name for template in response.templates]
    assert response.context["tasks_and_documents"].number == 2


@pytest.mark.django_db
def test_encounter_details_other_encounters_pagination(provider: User, organization: Organization, patient):
    """Test that other encounters are paginated correctly."""
    # Create 15 encounters for the patient
    encounters = []
    for _i in range(15):
        enc = Encounter.objects.create(patient=patient, organization=organization, status=EncounterStatus.IN_PROGRESS)
        encounters.append(enc)

    # Use the first encounter as the current one
    current_encounter = encounters[0]

    client = Client()
    client.force_login(provider)
    url = reverse(
        "providers:encounter", kwargs={"organization_id": organization.id, "encounter_id": current_encounter.id}
    )

    # Test first page - should have 5 other encounters (excluding current one)
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.context["other_encounters"]) == 5
    assert response.context["other_encounters"].number == 1
    assert response.context["other_encounters"].paginator.num_pages == 3

    # Test second page
    response = client.get(url + "?encounters_page=2")
    assert response.status_code == 200
    assert len(response.context["other_encounters"]) == 5
    assert response.context["other_encounters"].number == 2

    # Test third page
    response = client.get(url + "?encounters_page=3")
    assert response.status_code == 200
    assert len(response.context["other_encounters"]) == 4
    assert response.context["other_encounters"].number == 3


@pytest.mark.django_db
def test_encounter_details_other_encounters_htmx_pagination(provider: User, organization: Organization, patient):
    """Test that HTMX requests for other encounters return only the section template."""
    # Create 15 encounters
    encounters = []
    for _i in range(15):
        enc = Encounter.objects.create(patient=patient, organization=organization, status=EncounterStatus.IN_PROGRESS)
        encounters.append(enc)

    current_encounter = encounters[0]

    client = Client()
    client.force_login(provider)
    url = reverse(
        "providers:encounter", kwargs={"organization_id": organization.id, "encounter_id": current_encounter.id}
    )

    # Test HTMX request for other encounters section
    response = client.get(url + "?section=encounters&encounters_page=2", HTTP_HX_REQUEST="true")
    assert response.status_code == 200
    assert "provider/partials/other_encounters_section.html" in [template.name for template in response.templates]
    assert response.context["other_encounters"].number == 2


@pytest.mark.django_db
def test_encounter_details_multi_section_pagination_independence(
    provider: User, organization: Organization, encounter: Encounter
):
    """Test that pagination parameters for different sections don't interfere with each other."""
    # Create data for multiple sections
    for _i in range(15):
        SummaryFactory.create(patient=encounter.patient, organization=organization, encounter=encounter)
        TaskFactory.create(patient=encounter.patient, encounter=encounter)

    client = Client()
    client.force_login(provider)
    url = reverse("providers:encounter", kwargs={"organization_id": organization.id, "encounter_id": encounter.id})

    # Test that we can navigate to different pages in different sections simultaneously
    response = client.get(url + "?summaries_page=2&forms_page=1")
    assert response.status_code == 200
    assert response.context["summaries"].number == 2
    assert response.context["tasks_and_documents"].number == 1

    # Test another combination
    response = client.get(url + "?summaries_page=1&forms_page=2")
    assert response.status_code == 200
    assert response.context["summaries"].number == 1
    assert response.context["tasks_and_documents"].number == 2
