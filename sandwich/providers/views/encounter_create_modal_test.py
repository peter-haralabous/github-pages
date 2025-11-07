from datetime import date
from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from guardian.shortcuts import assign_perm
from playwright.sync_api import Page

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models.organization import Organization
from sandwich.core.models.patient import Patient
from sandwich.users.models import User


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
def test_encounter_create_modal_opens_with_button(live_server, provider_page: Page, organization: Organization):
    """Test that the encounter create command palette opens when 'New Encounter' button is clicked."""
    provider_page.goto(
        f"{live_server.url}{reverse('providers:encounter_list', kwargs={'organization_id': organization.id})}"
    )
    provider_page.wait_for_load_state("networkidle")

    # Click the "New Encounter" button
    new_encounter_btn = provider_page.locator("#new-encounter-btn")
    new_encounter_btn.click()

    # Wait for command palette to open - check the isOpen property via JavaScript
    is_open = provider_page.wait_for_function(
        "() => document.querySelector('command-palette')?.isOpen === true", timeout=2000
    )

    # Verify command palette is open
    assert is_open


@pytest.mark.e2e
def test_encounter_create_patient_form_no_longer_redirects_to_encounter_page(
    live_server, provider_page: Page, organization: Organization
):
    """Test that creating a patient no longer redirects to the encounter create page.

    With the new POC approach, patients are created normally and encounters
    can be created via the command palette afterward.
    """
    # Navigate to patient add page without return_url
    provider_page.goto(
        f"{live_server.url}{reverse('providers:patient_add', kwargs={'organization_id': organization.id})}"
    )
    provider_page.wait_for_load_state("networkidle")

    # Fill out patient form
    first_name_input = provider_page.locator("#id_first_name")
    first_name_input.fill("Test")

    last_name_input = provider_page.locator("#id_last_name")
    last_name_input.fill("Patient")

    dob_input = provider_page.locator("#id_date_of_birth")
    dob_input.fill("1990-01-01")

    email_input = provider_page.locator("#id_email")
    email_input.fill("test.patient@example.com")

    # Count patients before
    patients_before = Patient.objects.filter(organization=organization).count()

    # Submit the form
    submit_button = provider_page.get_by_role("button", name="Submit")
    submit_button.click()

    # Should redirect to patient details page, not encounter create
    provider_page.wait_for_url(lambda url: "/patient/" in url and "/encounter" not in url, timeout=5000)

    # Verify patient was created
    patients_after = Patient.objects.filter(organization=organization).count()
    assert patients_after == patients_before + 1


@pytest.mark.e2e
def test_encounter_modal_opens_via_htmx(live_server, provider_page: Page, organization: Organization, provider: User):
    """Test that clicking a patient in the command palette results loads the encounter modal via HTMX."""
    # Create a patient and assign view permission
    patient = PatientFactory.create(organization=organization, first_name="John", last_name="Doe")
    assign_perm("view_patient", provider, patient)
    assign_perm("create_encounter", provider, organization)

    # Navigate to encounter list
    provider_page.goto(
        f"{live_server.url}{reverse('providers:encounter_list', kwargs={'organization_id': organization.id})}"
    )
    provider_page.wait_for_load_state("networkidle")

    # Click the "New Encounter" button to open command palette
    new_encounter_btn = provider_page.locator("#new-encounter-btn")
    new_encounter_btn.click()

    # Wait for command palette to open
    provider_page.wait_for_function("() => document.querySelector('command-palette')?.isOpen === true", timeout=2000)

    # The command palette is in shadow DOM, but we can use evaluate to interact with it
    # Get the search URL and trigger a search directly
    search_url = (
        f"{live_server.url}{reverse('providers:encounter_create_search', kwargs={'organization_id': organization.id})}"
    )

    # Manually make the search request to get results with the patient
    response = provider_page.request.get(f"{search_url}?q=John&context=encounter_create")
    assert response.ok

    # Now we can click the patient link which should have hx-get attribute
    # This will be outside shadow DOM once HTMX loads it
    provider_page.evaluate(f"""
        fetch('{search_url}?q=John&context=encounter_create')
            .then(r => r.text())
            .then(html => {{
                const palette = document.querySelector('command-palette');
                if (palette && palette.shadowRoot) {{
                    const resultsUl = palette.shadowRoot.querySelector('.palette-results ul');
                    if (resultsUl) {{
                        resultsUl.innerHTML = html;
                    }}
                }}
            }});
    """)

    # Wait a moment for results to load
    provider_page.wait_for_timeout(500)

    # Now click on the patient link via JavaScript (since it's in shadow DOM)
    provider_page.evaluate("""
        const palette = document.querySelector('command-palette');
        if (palette && palette.shadowRoot) {
            const patientLink = palette.shadowRoot.querySelector('a[hx-get]');
            if (patientLink) {
                patientLink.click();
            }
        }
    """)

    # Wait for modal to appear in the modal-container
    provider_page.wait_for_selector("#encounter-create-modal", state="visible", timeout=3000)

    # Verify modal content shows patient info
    modal_content = provider_page.locator("#encounter-create-modal")
    assert "John" in modal_content.inner_text()
    assert "Doe" in modal_content.inner_text()


@pytest.mark.e2e
def test_create_patient_from_encounter_modal(
    live_server, provider_page: Page, organization: Organization, provider: User
):
    """Test creating a new patient from the encounter creation command palette."""
    assign_perm("create_patient", provider, organization)
    assign_perm("create_encounter", provider, organization)

    # Navigate to encounter list
    provider_page.goto(
        f"{live_server.url}{reverse('providers:encounter_list', kwargs={'organization_id': organization.id})}"
    )
    provider_page.wait_for_load_state("networkidle")

    # Count patients before
    patients_before = Patient.objects.filter(organization=organization).count()

    # Click the "New Encounter" button to open command palette
    new_encounter_btn = provider_page.locator("#new-encounter-btn")
    new_encounter_btn.click()

    # Wait for command palette to open
    provider_page.wait_for_function("() => document.querySelector('command-palette')?.isOpen === true", timeout=2000)

    # Type a search query into the command palette input (in shadow DOM)
    # This should trigger the search and show "Create patient" option
    provider_page.evaluate("""
        const palette = document.querySelector('command-palette');
        if (palette && palette.shadowRoot) {
            const input = palette.shadowRoot.querySelector('.palette-input');
            if (input) {
                input.value = 'NewPatient';
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }
    """)

    # Wait for search results to populate (debounced, so wait a bit)
    provider_page.wait_for_timeout(300)

    # Now select and click the "Create patient" link using keyboard (Arrow Down + Enter)
    # First, press ArrowDown to select the first result
    provider_page.evaluate("""
        const palette = document.querySelector('command-palette');
        if (palette && palette.shadowRoot) {
            const input = palette.shadowRoot.querySelector('.palette-input');
            if (input) {
                input.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }));
            }
        }
    """)

    # Small delay for selection to update
    provider_page.wait_for_timeout(50)

    # Press Enter to "click" the selected link
    provider_page.evaluate("""
        const palette = document.querySelector('command-palette');
        if (palette && palette.shadowRoot) {
            const input = palette.shadowRoot.querySelector('.palette-input');
            if (input) {
                input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
            }
        }
    """)

    # Wait for patient add modal to appear
    provider_page.wait_for_selector("#patient-add-modal", state="visible", timeout=5000)

    # Fill out the patient form
    provider_page.locator("#patient-add-modal #id_first_name").fill("Jane")
    provider_page.locator("#patient-add-modal #id_last_name").fill("NewPatient")
    provider_page.locator("#patient-add-modal #id_date_of_birth").fill("1995-03-20")
    provider_page.locator("#patient-add-modal #id_province").select_option("BC")
    provider_page.locator("#patient-add-modal #id_phn").fill("9333333339")

    # Submit the form
    provider_page.locator("#patient-add-modal input[type='submit']").click()

    # Wait for encounter create modal to appear with the new patient
    provider_page.wait_for_selector("#encounter-create-modal", state="visible", timeout=5000)

    # Verify encounter modal shows the newly created patient
    encounter_modal = provider_page.locator("#encounter-create-modal")
    modal_text = encounter_modal.inner_text()
    assert "Jane" in modal_text
    assert "NewPatient" in modal_text

    # Verify patient was created in database
    patients_after = Patient.objects.filter(organization=organization).count()
    assert patients_after == patients_before + 1

    # Verify the specific patient exists
    new_patient = Patient.objects.get(first_name="Jane", last_name="NewPatient")
    assert new_patient.organization == organization
    assert provider.has_perm("view_patient", new_patient)


# Unit tests for patient_add_modal view (encounter creation flow)


def test_patient_add_modal_get(provider: User, organization: Organization) -> None:
    """Test GET request to patient_add_modal returns modal with form."""
    client = Client()
    client.force_login(provider)
    res = client.get(
        reverse(
            "providers:patient_add_modal",
            kwargs={"organization_id": organization.id},
        )
    )

    assert res.status_code == HTTPStatus.OK
    assert b"Create Patient" in res.content
    assert b"patient-add-modal" in res.content


def test_patient_add_modal_get_with_maybe_name(provider: User, organization: Organization) -> None:
    """Test GET request with maybe_name parameter pre-fills form fields."""
    client = Client()
    client.force_login(provider)
    res = client.get(
        reverse(
            "providers:patient_add_modal",
            kwargs={"organization_id": organization.id},
        )
        + "?maybe_name=John+Doe"
    )

    assert res.status_code == HTTPStatus.OK
    assert b"John" in res.content
    assert b"Doe" in res.content


def test_patient_add_modal_post_success(provider: User, organization: Organization) -> None:
    """Test POST request to patient_add_modal creates patient and returns encounter modal."""
    data = {
        "first_name": "Jane",
        "last_name": "Modal",
        "date_of_birth": date(1990, 5, 15),
        "province": "BC",
        "phn": "9222222228",
    }

    client = Client()
    client.force_login(provider)
    res = client.post(
        reverse(
            "providers:patient_add_modal",
            kwargs={"organization_id": organization.id},
        ),
        data=data,
    )

    assert res.status_code == HTTPStatus.OK
    # Should return encounter modal with selected patient
    assert b"encounter-create-modal" in res.content
    assert b"Jane" in res.content
    assert b"Modal" in res.content

    # Verify patient was created
    created_patient = Patient.objects.get(last_name="Modal")
    assert created_patient.first_name == "Jane"
    assert created_patient.organization == organization
    assert provider.has_perm("view_patient", created_patient)
    assert provider.has_perm("create_task", created_patient)


def test_patient_add_modal_post_invalid_data(provider: User, organization: Organization) -> None:
    """Test POST request with invalid data re-renders modal with errors."""
    data = {
        "first_name": "Jane",
        "last_name": "Modal",
        # Missing required date_of_birth
        "province": "BC",
    }

    client = Client()
    client.force_login(provider)
    res = client.post(
        reverse(
            "providers:patient_add_modal",
            kwargs={"organization_id": organization.id},
        ),
        data=data,
    )

    assert res.status_code == HTTPStatus.OK
    # Should re-render the patient add modal with errors
    assert b"patient-add-modal" in res.content
    # Should not create patient
    assert not Patient.objects.filter(last_name="Modal").exists()


def test_patient_add_modal_deny_access_not_provider(user: User, organization: Organization) -> None:
    """Test non-provider cannot access patient_add_modal."""
    data = {
        "first_name": "Jane",
        "last_name": "Modal",
        "date_of_birth": date(1990, 5, 15),
        "province": "BC",
        "phn": "9222222228",
    }

    client = Client()
    client.force_login(user)
    res = client.post(
        reverse(
            "providers:patient_add_modal",
            kwargs={"organization_id": organization.id},
        ),
        data=data,
    )

    assert res.status_code == HTTPStatus.NOT_FOUND
    assert not Patient.objects.filter(last_name="Modal").exists()
