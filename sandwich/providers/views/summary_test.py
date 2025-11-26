import pytest
from django.test import Client
from django.urls import reverse
from guardian.shortcuts import assign_perm
from playwright.sync_api import Page
from playwright.sync_api import expect

from sandwich.core.factories.form import FormFactory
from sandwich.core.factories.patient import PatientFactory
from sandwich.core.factories.summary import SummaryFactory
from sandwich.core.factories.summary_template import SummaryTemplateFactory
from sandwich.core.factories.task import TaskFactory
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.form_submission import FormSubmission
from sandwich.core.models.form_submission import FormSubmissionStatus
from sandwich.core.models.organization import Organization
from sandwich.core.models.summary import Summary
from sandwich.core.models.summary import SummaryStatus
from sandwich.core.models.task import TaskStatus
from sandwich.core.service.summary_service import trigger_summary_generation
from sandwich.users.models import User


@pytest.mark.django_db
def test_summary_detail_requires_authentication(
    user: User, organization: Organization, patient, encounter: Encounter
) -> None:
    summary = SummaryFactory.create(
        patient=patient,
        encounter=encounter,
        organization=organization,
        title="Test Summary",
        body="<p>Test content</p>",
    )

    client = Client()
    url = reverse("providers:summary_detail", kwargs={"organization_id": organization.id, "summary_id": summary.id})
    result = client.get(url)

    assert result.status_code == 302
    assert "/login/" in result.url  # type: ignore[attr-defined]


@pytest.mark.django_db
def test_summary_detail_not_found_without_view_summary_permission(user: User, organization: Organization) -> None:
    random_patient = PatientFactory.create()
    summary = SummaryFactory.create(
        patient=random_patient,
        organization=organization,
        title="Test Summary",
        body="<p>Test content</p>",
    )

    client = Client()
    client.force_login(user)

    url = reverse("providers:summary_detail", kwargs={"organization_id": organization.id, "summary_id": summary.id})
    result = client.get(url)

    assert result.status_code == 404


@pytest.mark.django_db
def test_summary_detail_renders_template(
    provider: User, organization: Organization, patient, encounter: Encounter
) -> None:
    summary = SummaryFactory.create(
        patient=patient,
        encounter=encounter,
        organization=organization,
        title="Test Summary",
        body="<p>Test content</p>",
    )
    assign_perm("view_summary", provider, summary)

    client = Client()
    client.force_login(provider)
    url = reverse("providers:summary_detail", kwargs={"organization_id": organization.id, "summary_id": summary.id})
    result = client.get(url)

    assert result.status_code == 200
    assert "provider/summary_detail.html" in [template.name for template in result.templates]


@pytest.mark.django_db
def test_summary_detail_with_encounter_context(
    provider: User, organization: Organization, patient, encounter: Encounter
) -> None:
    summary = SummaryFactory.create(
        patient=patient,
        encounter=encounter,
        organization=organization,
        title="Encounter Summary",
        body="<p>Encounter-related content</p>",
    )
    assign_perm("view_summary", provider, summary)

    client = Client()
    client.force_login(provider)
    url = reverse("providers:summary_detail", kwargs={"organization_id": organization.id, "summary_id": summary.id})
    result = client.get(url)

    assert result.status_code == 200
    assert result.context is not None
    assert result.context["summary"] == summary
    assert result.context["patient"] == patient
    assert result.context["encounter"] == encounter
    assert result.context["organization"] == organization
    assert result.context["breadcrumb_text"] == "Back to encounter"

    # Verify breadcrumb URL points to encounter details
    expected_breadcrumb_url = reverse(
        "providers:encounter",
        kwargs={"organization_id": organization.id, "encounter_id": encounter.id},
    )
    assert result.context["breadcrumb_url"] == expected_breadcrumb_url


@pytest.mark.django_db
def test_summary_detail_without_encounter_context(provider: User, organization: Organization, patient) -> None:
    summary = SummaryFactory.create(
        patient=patient,
        encounter=None,
        organization=organization,
        title="Patient Summary",
        body="<p>Patient-related content</p>",
    )
    assign_perm("view_summary", provider, summary)

    client = Client()
    client.force_login(provider)
    url = reverse("providers:summary_detail", kwargs={"organization_id": organization.id, "summary_id": summary.id})
    result = client.get(url)

    assert result.status_code == 200
    assert result.context is not None
    assert result.context["summary"] == summary
    assert result.context["patient"] == patient
    assert result.context["encounter"] is None
    assert result.context["organization"] == organization
    assert result.context["breadcrumb_text"] == "Back to patient"

    # Verify breadcrumb URL points to patient details
    expected_breadcrumb_url = reverse(
        "providers:patient",
        kwargs={"organization_id": organization.id, "patient_id": patient.id},
    )
    assert result.context["breadcrumb_url"] == expected_breadcrumb_url


@pytest.mark.django_db
def test_summary_detail_summary_with_different_statuses(provider: User, organization: Organization, patient) -> None:
    for status in [SummaryStatus.PENDING, SummaryStatus.PROCESSING, SummaryStatus.SUCCEEDED, SummaryStatus.FAILED]:
        summary = SummaryFactory.create(
            patient=patient,
            organization=organization,
            title=f"Summary with {status} status",
            body="<p>Content</p>",
            status=status,
        )
        assign_perm("view_summary", provider, summary)

        client = Client()
        client.force_login(provider)
        url = reverse(
            "providers:summary_detail", kwargs={"organization_id": organization.id, "summary_id": summary.id}
        )
        result = client.get(url)

        assert result.status_code == 200
        assert result.context["summary"].status == status


@pytest.mark.django_db
def test_summary_detail_htmx_request_returns_modal(
    provider: User, organization: Organization, patient, encounter: Encounter
) -> None:
    summary = SummaryFactory.create(
        patient=patient,
        encounter=encounter,
        organization=organization,
        title="Test Summary",
        body="<p>Test content</p>",
    )
    assign_perm("view_summary", provider, summary)

    client = Client()
    client.force_login(provider)
    url = reverse("providers:summary_detail", kwargs={"organization_id": organization.id, "summary_id": summary.id})

    result = client.get(url, HTTP_HX_REQUEST="true")

    assert result.status_code == 200
    assert "provider/partials/summary_modal.html" in [template.name for template in result.templates]
    # Modal doesn't need breadcrumb context
    assert "breadcrumb_url" not in result.context
    assert "breadcrumb_text" not in result.context


@pytest.mark.django_db
def test_summary_detail_modal_includes_cleanup_script(
    provider: User, organization: Organization, patient, encounter: Encounter
) -> None:
    """Verify that the modal includes JavaScript to remove itself from DOM when closed."""
    summary = SummaryFactory.create(
        patient=patient,
        encounter=encounter,
        organization=organization,
        title="Test Summary",
        body="<p>Test content</p>",
    )
    assign_perm("view_summary", provider, summary)

    client = Client()
    client.force_login(provider)
    url = reverse("providers:summary_detail", kwargs={"organization_id": organization.id, "summary_id": summary.id})

    result = client.get(url, HTTP_HX_REQUEST="true")

    assert result.status_code == 200
    content = result.content.decode("utf-8")

    # Verify the modal has the correct ID
    assert 'id="summary-modal"' in content

    # Verify the cleanup script is present
    assert 'modal.addEventListener("close"' in content
    assert "modal.remove()" in content
    assert "once: true" in content  # Flexible to handle different formatting


@pytest.mark.django_db
def test_summary_detail_regular_request_returns_full_page(
    provider: User, organization: Organization, patient, encounter: Encounter
) -> None:
    summary = SummaryFactory.create(
        patient=patient,
        encounter=encounter,
        organization=organization,
        title="Test Summary",
        body="<p>Test content</p>",
    )
    assign_perm("view_summary", provider, summary)

    client = Client()
    client.force_login(provider)
    url = reverse("providers:summary_detail", kwargs={"organization_id": organization.id, "summary_id": summary.id})

    result = client.get(url)

    assert result.status_code == 200
    assert "provider/summary_detail.html" in [template.name for template in result.templates]
    # Full page has breadcrumb context
    assert "breadcrumb_url" in result.context
    assert "breadcrumb_text" in result.context


@pytest.mark.django_db
def test_summary_card_shows_different_statuses(provider: User, organization: Organization, patient) -> None:
    pending_summary = SummaryFactory.create(
        patient=patient,
        organization=organization,
        title="Pending Summary",
        status=SummaryStatus.PENDING,
    )
    assign_perm("view_summary", provider, pending_summary)

    processing_summary = SummaryFactory.create(
        patient=patient,
        organization=organization,
        title="Processing Summary",
        status=SummaryStatus.PROCESSING,
    )
    assign_perm("view_summary", provider, processing_summary)

    succeeded_summary = SummaryFactory.create(
        patient=patient,
        organization=organization,
        title="Succeeded Summary",
        status=SummaryStatus.SUCCEEDED,
        body="<p>Complete summary content</p>",
    )
    assign_perm("view_summary", provider, succeeded_summary)

    failed_summary = SummaryFactory.create(
        patient=patient,
        organization=organization,
        title="Failed Summary",
        status=SummaryStatus.FAILED,
    )
    assign_perm("view_summary", provider, failed_summary)

    client = Client()
    client.force_login(provider)
    url = reverse("providers:patient", kwargs={"organization_id": organization.id, "patient_id": patient.id})
    response = client.get(url)

    assert response.status_code == 200
    content = response.content.decode()

    assert "Pending Summary" in content
    assert "Processing Summary" in content
    assert "Succeeded Summary" in content
    assert "Failed Summary" in content

    assert "Pending" in content
    assert "Processing" in content
    assert "Succeeded" in content
    assert "Failed" in content

    assert (
        reverse(
            "providers:summary_detail", kwargs={"organization_id": organization.id, "summary_id": pending_summary.id}
        )
        in content
    )
    assert (
        reverse(
            "providers:summary_detail",
            kwargs={"organization_id": organization.id, "summary_id": processing_summary.id},
        )
        in content
    )
    assert (
        reverse(
            "providers:summary_detail", kwargs={"organization_id": organization.id, "summary_id": succeeded_summary.id}
        )
        in content
    )
    assert (
        reverse(
            "providers:summary_detail", kwargs={"organization_id": organization.id, "summary_id": failed_summary.id}
        )
        in content
    )


@pytest.mark.e2e
@pytest.mark.django_db
def test_summary_workflow_end_to_end(  # noqa: PLR0915
    live_server, provider_page: Page, organization: Organization, provider: User, encounter: Encounter
) -> None:
    """
    Test the complete summary workflow end-to-end:
    1. Create form and summary template
    2. Create task for patient
    3. Submit task (creates form submission)
    4. Verify summary is generated
    5. Navigate to patient details page
    6. Click on summary card to view details
    7. Verify summary content is displayed
    8. Verify breadcrumb navigation works
    """
    patient = encounter.patient

    # 1. Create form with schema
    schema = {
        "elements": [
            {"type": "text", "name": "chiefComplaint", "title": "What brings you in today?"},
            {"type": "text", "name": "symptoms", "title": "Describe your symptoms"},
        ]
    }
    form = FormFactory.create(name="Patient Intake Form", schema=schema, organization=organization)

    # 2. Create summary template
    template_text = """
# Patient Visit Summary

**Patient:** {{ patient.first_name }} {{ patient.last_name }}

**Chief Complaint:** {{ submission.data.chiefComplaint }}

**Symptoms:** {{ submission.data.symptoms }}

**Status:** {{ submission.status }}
"""
    template = SummaryTemplateFactory.create(
        organization=organization,
        form=form,
        name="Visit Summary",
        text=template_text,
    )

    # 3. Create task for patient
    task = TaskFactory.create(
        patient=patient,
        encounter=encounter,
        form_version=form.get_current_version(),
        status=TaskStatus.READY,
    )

    # 4. Simulate form submission (normally done by patient)
    submission = FormSubmission.objects.create(
        task=task,
        patient=patient,
        status=FormSubmissionStatus.COMPLETED,
        data={
            "chiefComplaint": "Severe headache",
            "symptoms": "Throbbing pain on left side of head for 2 days",
        },
    )

    # 5. Trigger summary generation
    trigger_summary_generation(submission)

    # Wait for summary to be created
    try:
        summary = Summary.objects.get(
            submission=submission,
            template=template,
            patient=patient,
        )
    except Summary.DoesNotExist:
        pytest.fail("Expected summary to be created but none was found")
    except Summary.MultipleObjectsReturned:
        pytest.fail("Expected exactly one summary, found multiple")

    # Manually mark summary as succeeded and set body (simulating async task completion)
    summary.status = SummaryStatus.SUCCEEDED
    summary.body = f"""
<h1>Patient Visit Summary</h1>
<p><strong>Patient:</strong> {patient.first_name} {patient.last_name}</p>
<p><strong>Chief Complaint:</strong> Severe headache</p>
<p><strong>Symptoms:</strong> Throbbing pain on left side of head for 2 days</p>
<p><strong>Status:</strong> completed</p>
"""
    summary.save()

    # 6. Navigate to patient details page
    patient_url = (
        f"{live_server.url}"
        f"{reverse('providers:patient', kwargs={'organization_id': organization.id, 'patient_id': patient.id})}"
    )
    provider_page.goto(patient_url)
    provider_page.wait_for_load_state("networkidle")

    # 7. Verify summaries section is visible
    summaries_section = provider_page.locator("text=Summaries")
    expect(summaries_section).to_be_visible()

    # 8. Find and click on the summary card
    summary_card = provider_page.locator(f"text={summary.title}").locator("xpath=ancestor::a").first
    expect(summary_card).to_be_visible()

    # Verify status badge is shown
    status_badge = provider_page.locator(".badge", has_text="Succeeded")
    expect(status_badge).to_be_visible()

    # Click the summary card
    summary_card.click()
    provider_page.wait_for_timeout(500)  # Wait for HTMX to load modal

    # 9. Verify modal is displayed (not navigated to new page)
    modal = provider_page.locator("#summary-modal")
    expect(modal).to_be_visible()

    # Verify modal contains summary title
    modal_title = modal.locator("h3", has_text="Visit Summary")
    expect(modal_title).to_be_visible()

    # Verify patient name is in the modal
    patient_name_in_modal = modal.locator(f"text={patient.first_name} {patient.last_name}")
    expect(patient_name_in_modal).to_be_visible()

    # Verify chief complaint is displayed in modal
    chief_complaint_in_modal = modal.locator("text=Severe headache")
    expect(chief_complaint_in_modal).to_be_visible()

    # Verify symptoms are displayed in modal
    symptoms_in_modal = modal.locator("text=Throbbing pain on left side of head for 2 days")
    expect(symptoms_in_modal).to_be_visible()

    # 10. Test "Open Full Page" button in modal
    open_full_page_btn = modal.locator("a.btn-primary", has_text="Open Full Page")
    expect(open_full_page_btn).to_be_visible()

    # Open in new context to test full page (simulates opening in new tab)
    with provider_page.context.new_page() as new_page:
        detail_path = reverse(
            "providers:summary_detail", kwargs={"organization_id": organization.id, "summary_id": summary.id}
        )
        full_page_url = f"{live_server.url}{detail_path}"
        new_page.goto(full_page_url)
        new_page.wait_for_load_state("networkidle")

        # Verify we're on the summary detail page
        assert new_page.url == full_page_url

        # Verify full page content is displayed
        page_title = new_page.locator("h1", has_text="Patient Visit Summary")
        expect(page_title).to_be_visible()

        # 11. Verify breadcrumb navigation on full page
        breadcrumb_link = new_page.locator("a", has_text="Back to encounter")
        expect(breadcrumb_link).to_be_visible()

        # Click breadcrumb to go back to encounter
        breadcrumb_link.click()
        new_page.wait_for_load_state("networkidle")

        # Verify we're back on the encounter details page
        expected_encounter_url = reverse(
            "providers:encounter", kwargs={"organization_id": organization.id, "encounter_id": encounter.id}
        )
        assert expected_encounter_url in new_page.url, (
            f"Expected to navigate to encounter page but got: {new_page.url}"
        )

    # 12. Back on original page, close the modal
    close_button = modal.locator("button.btn-circle")
    expect(close_button).to_be_visible()
    close_button.click()

    # Verify modal is closed/removed
    provider_page.wait_for_timeout(300)
    expect(modal).not_to_be_visible()


@pytest.mark.e2e
@pytest.mark.django_db
def test_summary_modal_cleanup_when_opening_multiple_summaries(
    live_server, provider_page: Page, organization: Organization, provider: User, encounter: Encounter
) -> None:
    """
    Test that opening multiple summary modals in sequence shows the correct content each time.
    This prevents regression of a bug where stale modals accumulated in the DOM, causing
    subsequent summary clicks to show the first summary's content instead of the new one.
    """
    patient = encounter.patient

    # Create two different summaries with distinct content
    summary1 = SummaryFactory.create(
        patient=patient,
        encounter=encounter,
        organization=organization,
        title="First Summary",
        body="<p>This is the first summary content</p>",
        status=SummaryStatus.SUCCEEDED,
    )
    assign_perm("view_summary", provider, summary1)

    summary2 = SummaryFactory.create(
        patient=patient,
        encounter=encounter,
        organization=organization,
        title="Second Summary",
        body="<p>This is the second summary content</p>",
        status=SummaryStatus.SUCCEEDED,
    )
    assign_perm("view_summary", provider, summary2)

    # Navigate to patient details page
    patient_url = (
        f"{live_server.url}"
        f"{reverse('providers:patient', kwargs={'organization_id': organization.id, 'patient_id': patient.id})}"
    )
    provider_page.goto(patient_url)
    provider_page.wait_for_load_state("networkidle")

    # Open first summary modal
    first_summary_card = provider_page.locator(f"text={summary1.title}").locator("xpath=ancestor::a").first
    expect(first_summary_card).to_be_visible()
    first_summary_card.click()
    provider_page.wait_for_timeout(500)

    # Verify first summary modal is displayed with correct content
    modal = provider_page.locator("#summary-modal")
    expect(modal).to_be_visible()
    expect(modal.locator("text=This is the first summary content")).to_be_visible()
    expect(modal.locator("text=This is the second summary content")).not_to_be_visible()

    # Verify only one modal exists in the DOM
    all_modals = provider_page.locator("#summary-modal").all()
    assert len(all_modals) == 1, f"Expected exactly 1 modal in DOM, found {len(all_modals)}"

    # Close the first modal
    close_button = modal.locator("button.btn-circle")
    close_button.click()
    provider_page.wait_for_timeout(300)

    # Verify modal is removed from DOM (not just hidden)
    all_modals_after_close = provider_page.locator("#summary-modal").all()
    assert len(all_modals_after_close) == 0, (
        f"Expected modal to be removed from DOM after closing, but found {len(all_modals_after_close)} modals"
    )

    # Open second summary modal
    second_summary_card = provider_page.locator(f"text={summary2.title}").locator("xpath=ancestor::a").first
    expect(second_summary_card).to_be_visible()
    second_summary_card.click()
    provider_page.wait_for_timeout(500)

    # Verify second summary modal is displayed with correct content
    modal_after_reopen = provider_page.locator("#summary-modal")
    expect(modal_after_reopen).to_be_visible()
    expect(modal_after_reopen.locator("text=This is the second summary content")).to_be_visible()
    expect(modal_after_reopen.locator("text=This is the first summary content")).not_to_be_visible()

    # Verify still only one modal exists in the DOM
    all_modals_final = provider_page.locator("#summary-modal").all()
    assert len(all_modals_final) == 1, f"Expected exactly 1 modal in DOM, found {len(all_modals_final)}"

    # Close the second modal
    close_button_2 = modal_after_reopen.locator("button.btn-circle")
    close_button_2.click()
    provider_page.wait_for_timeout(300)

    # Verify modal is removed from DOM
    all_modals_end = provider_page.locator("#summary-modal").all()
    assert len(all_modals_end) == 0, (
        f"Expected modal to be removed from DOM after closing, but found {len(all_modals_end)} modals"
    )
