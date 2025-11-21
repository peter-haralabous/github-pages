import pytest
from django.urls import reverse
from guardian.shortcuts import assign_perm
from playwright.sync_api import Page

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models.organization import Organization
from sandwich.core.models.patient import Patient
from sandwich.users.models import User


@pytest.mark.e2e
@pytest.mark.django_db
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
@pytest.mark.django_db
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
@pytest.mark.django_db
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

    provider_page.wait_for_load_state("networkidle")

    # Verify we're now looking at the created patient
    heading = provider_page.locator("#content h1")
    assert "NewPatient, Jane" in heading.inner_text()

    # Verify patient was created in database
    patients_after = Patient.objects.filter(organization=organization).count()
    assert patients_after == patients_before + 1

    # Verify the specific patient exists
    new_patient = Patient.objects.get(first_name="Jane", last_name="NewPatient")
    assert new_patient.organization == organization
    assert provider.has_perm("view_patient", new_patient)
