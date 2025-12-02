"""Tests for summary service including integration and E2E tests."""

import uuid
from unittest.mock import MagicMock
from unittest.mock import patch
from urllib.parse import urlparse

import pytest
from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY
from django.contrib.auth import HASH_SESSION_KEY
from django.contrib.auth import SESSION_KEY
from django.contrib.sessions.backends.db import SessionStore
from django.urls import reverse
from django.utils import timezone
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
from sandwich.core.models.patient import Patient
from sandwich.core.models.summary import Summary
from sandwich.core.models.summary import SummaryStatus
from sandwich.core.service.summary_service import generate_summary_task
from sandwich.core.service.summary_service import render_summary_template
from sandwich.core.service.summary_service import trigger_summary_generation
from sandwich.users.models import User


@pytest.fixture
def mock_job_context():
    """Mock job context for testing summary generation tasks."""
    context = MagicMock()
    context.job.id = 1
    context.job.task_name = "generate_summary_task"
    return context


@pytest.fixture
def auth_provider_cookies(provider, transactional_db, live_server, page):
    """Create a Django session for provider user and add its auth cookies to Playwright page."""
    session = SessionStore()
    session[SESSION_KEY] = str(provider.pk)
    session[BACKEND_SESSION_KEY] = "django.contrib.auth.backends.ModelBackend"
    session[HASH_SESSION_KEY] = provider.get_session_auth_hash()
    session.save()

    parsed = urlparse(live_server.url)
    domain = parsed.hostname or "localhost"

    cookie = {
        "name": settings.SESSION_COOKIE_NAME,
        "value": session.session_key,
        "domain": domain,
        "path": "/",
        "httpOnly": True,
    }

    page.context.add_cookies([cookie])
    return [cookie]


def get_summary_url(summary: Summary) -> str:
    """Get summary detail URL."""
    return reverse(
        "providers:summary_detail",
        kwargs={"organization_id": str(summary.organization.id), "summary_id": str(summary.id)},
    )


# ============================================================================
# Unit Tests
# ============================================================================


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("template_text", "submission_data", "patient_kwargs", "expected_strings"),
    [
        # Basic patient data and submission fields
        (
            "# Summary for {{ patient.first_name }} {{ patient.last_name }}\n\n"
            "Complaint: {{ submission.data.chief_complaint }}",
            {"chief_complaint": "Headache", "duration": "3 days"},
            {"first_name": "John", "last_name": "Doe"},
            ["Summary for John Doe", "Complaint: Headache"],
        ),
        # Submission metadata
        (
            "Status: {{ submission.status }}\nSubmitted: {{ submission.submitted_at }}",
            {"symptom": "Fever"},
            {},
            ["Status: completed", "Submitted:"],
        ),
        # Nested data
        (
            "Temperature: {{ submission.data.vitals.temperature }}\nBP: {{ submission.data.vitals.blood_pressure }}",
            {"vitals": {"temperature": "98.6", "blood_pressure": "120/80"}},
            {},
            ["Temperature: 98.6", "BP: 120/80"],
        ),
        # Empty data
        (
            "Patient: {{ patient.first_name }}\nData: {{ submission.data }}",
            {},
            {"first_name": "Test"},
            ["Patient: Test"],
        ),
    ],
)
def test_render_summary_template(template_text, submission_data, patient_kwargs, expected_strings):
    patient = PatientFactory.create(**patient_kwargs)
    submission = FormSubmission.objects.create(
        patient=patient,
        status=FormSubmissionStatus.COMPLETED,
        data=submission_data,
    )
    submission.submitted_at = timezone.now()
    submission.save()

    template = SummaryTemplateFactory.create(text=template_text)
    result = render_summary_template(template, submission)

    for expected in expected_strings:
        assert expected in result


@pytest.mark.django_db
def test_render_summary_template_markdown_conversion():
    patient = PatientFactory.create()
    submission = FormSubmission.objects.create(
        patient=patient,
        status=FormSubmissionStatus.DRAFT,
        data={},
    )

    template = SummaryTemplateFactory.create(text="# Heading 1\n\n**Bold text**\n\n- List item 1\n- List item 2")
    result = render_summary_template(template, submission)

    assert "<h1>" in result
    assert "<strong>" in result
    assert "<ul>" in result or "<li>" in result


@pytest.mark.django_db
def test_trigger_summary_generation_creates_summaries():
    template = SummaryTemplateFactory.create(
        text="# Summary\n\nPatient: {{ patient.first_name }}",
        name="Test Summary",
    )
    task = TaskFactory.create(
        form_version=template.form.get_current_version(),
        patient__organization=template.organization,
    )
    submission = FormSubmission.objects.create(
        task=task,
        patient=task.patient,
        status=FormSubmissionStatus.COMPLETED,
        data={"answer": "test"},
    )

    with patch("sandwich.core.service.summary_service.generate_summary_task.defer") as mock_defer:
        trigger_summary_generation(submission)

    summaries = Summary.objects.filter(submission=submission, template=template)
    assert summaries.count() == 1

    summary = summaries.first()
    assert summary is not None
    assert summary.status == SummaryStatus.PENDING
    assert summary.patient == task.patient
    assert summary.organization == template.organization
    assert summary.encounter == task.encounter
    assert summary.title == "Test Summary"
    assert summary.body == ""
    mock_defer.assert_called_once_with(summary_id=str(summary.id))


@pytest.mark.django_db
def test_trigger_summary_generation_multiple_templates():
    template1 = SummaryTemplateFactory.create(text="# Summary 1", name="Summary One")
    SummaryTemplateFactory.create(
        form=template1.form,
        organization=template1.organization,
        text="# Summary 2",
        name="Summary Two",
    )
    task = TaskFactory.create(
        form_version=template1.form.get_current_version(),
        patient__organization=template1.organization,
    )
    submission = FormSubmission.objects.create(
        task=task,
        patient=task.patient,
        status=FormSubmissionStatus.COMPLETED,
        data={},
    )

    with patch("sandwich.core.service.summary_service.generate_summary_task.defer") as mock_defer:
        trigger_summary_generation(submission)

    assert Summary.objects.filter(submission=submission).count() == 2
    assert mock_defer.call_count == 2


@pytest.mark.django_db
def test_trigger_summary_generation_filters_by_organization():
    template1 = SummaryTemplateFactory.create(text="# Summary 1")
    SummaryTemplateFactory.create(form=template1.form, text="# Summary 2")  # Different organization

    task = TaskFactory.create(
        form_version=template1.form.get_current_version(),
        patient__organization=template1.organization,
    )
    submission = FormSubmission.objects.create(
        task=task,
        patient=task.patient,
        status=FormSubmissionStatus.COMPLETED,
        data={},
    )

    with patch("sandwich.core.service.summary_service.generate_summary_task.defer"):
        trigger_summary_generation(submission)

    summaries = Summary.objects.filter(submission=submission)
    assert summaries.count() == 1
    summary = summaries.first()
    assert summary is not None
    assert summary.template == template1


@pytest.mark.django_db
def test_trigger_summary_generation_no_task():
    patient = PatientFactory.create()
    submission = FormSubmission.objects.create(
        task=None,
        patient=patient,
        status=FormSubmissionStatus.COMPLETED,
        data={},
    )

    with patch("sandwich.core.service.summary_service.generate_summary_task.defer") as mock_defer:
        trigger_summary_generation(submission)

    assert Summary.objects.filter(submission=submission).count() == 0
    mock_defer.assert_not_called()


@pytest.mark.django_db(transaction=True)
def test_generate_summary_task_success(mock_job_context):
    template = SummaryTemplateFactory.create(
        text=(
            "# Summary\n\n"
            "Patient: {{ patient.first_name }} {{ patient.last_name }}\n"
            "Q1: {{ submission.data.question1 }}\n"
            "Q2: {{ submission.data.question2 }}"
        ),
    )
    patient = PatientFactory.create(
        first_name="Alice",
        last_name="Smith",
        organization=template.organization,
    )
    submission = FormSubmission.objects.create(
        patient=patient,
        status=FormSubmissionStatus.COMPLETED,
        data={"question1": "answer1", "question2": "answer2"},
    )
    summary = SummaryFactory.create(
        patient=patient,
        organization=template.organization,
        submission=submission,
        template=template,
        status=SummaryStatus.PENDING,
    )

    generate_summary_task(mock_job_context, summary_id=str(summary.id))

    summary.refresh_from_db()
    assert summary.status == SummaryStatus.SUCCEEDED
    assert summary.title == template.name
    assert "Patient: Alice Smith" in summary.body
    assert "Q1: answer1" in summary.body
    assert "Q2: answer2" in summary.body


@pytest.mark.django_db(transaction=True)
def test_generate_summary_task_error_handling(mock_job_context):
    temp_template = SummaryTemplateFactory.create()
    patient = PatientFactory.create(organization=temp_template.organization)
    submission = FormSubmission.objects.create(
        patient=patient,
        status=FormSubmissionStatus.COMPLETED,
        data={},
    )

    summary = SummaryFactory.create(
        patient=patient,
        organization=temp_template.organization,
        submission=submission,
        status=SummaryStatus.PENDING,
        template=None,
    )

    generate_summary_task(mock_job_context, summary_id=str(summary.id))

    summary.refresh_from_db()
    assert summary.status == SummaryStatus.FAILED


@pytest.mark.django_db(transaction=True)
def test_generate_summary_task_nonexistent_summary(mock_job_context):
    fake_id = str(uuid.uuid4())
    generate_summary_task(mock_job_context, summary_id=fake_id)
    assert not Summary.objects.filter(id=fake_id).exists()


@pytest.mark.django_db
def test_assign_default_summary_perms_for_providers(
    encounter: Encounter,
    patient: Patient,
    provider: User,
) -> None:
    assert patient.organization is not None
    template = SummaryTemplateFactory.create(organization=patient.organization)
    submission = FormSubmission.objects.create(
        patient=patient,
        status=FormSubmissionStatus.COMPLETED,
        data={},
    )
    summary = Summary.objects.create(
        patient=patient,
        organization=patient.organization,
        encounter=encounter,
        template=template,
        submission=submission,
        title="Test Summary",
        body="",
        status=SummaryStatus.PENDING,
    )

    assert provider.has_perm("view_summary", summary)


@pytest.mark.django_db
def test_assign_default_summary_perms_for_patient_user(
    patient: Patient,
) -> None:
    assert patient.organization is not None
    template = SummaryTemplateFactory.create(organization=patient.organization)
    submission = FormSubmission.objects.create(
        patient=patient,
        status=FormSubmissionStatus.COMPLETED,
        data={},
    )
    summary = Summary.objects.create(
        patient=patient,
        organization=patient.organization,
        encounter=None,
        template=template,
        submission=submission,
        title="Test Summary",
        body="",
        status=SummaryStatus.PENDING,
    )

    assert patient.user is not None
    assert patient.user.has_perm("view_summary", summary)


# ============================================================================
# Integration Tests (using VCR for real LLM responses)
# ============================================================================


@pytest.mark.vcr
@pytest.mark.django_db
def test_render_summary_template_with_ai_blocks():
    """Test rendering a template with AI blocks (two-pass rendering) using real LLM (via VCR)."""
    patient = PatientFactory.create(first_name="John", last_name="Doe")
    submission = FormSubmission.objects.create(
        patient=patient,
        status=FormSubmissionStatus.COMPLETED,
        data={
            "chief_complaint": "Severe headache for 3 days",
            "pain_scale": "8",
            "symptoms": ["nausea", "photophobia"],
        },
    )
    submission.submitted_at = timezone.now()
    submission.save()

    # Template with AI block
    template_text = """# Patient Summary for {{ patient.first_name }} {{ patient.last_name }}

{% ai "Clinical Assessment" %}
Based on the following patient data, provide a clinical assessment:
- Chief Complaint: {{ submission.data.chief_complaint }}
- Pain Scale: {{ submission.data.pain_scale }}/10
- Associated Symptoms: {{ submission.data.symptoms|join:", " }}
{% endai %}
"""

    template = SummaryTemplateFactory.create(text=template_text)
    result = render_summary_template(template, submission)

    # Verify AI content was rendered
    assert "Patient Summary for John Doe" in result
    # Should have generated clinical content
    assert len(result) > len("# Patient Summary for John Doe")


@pytest.mark.django_db
def test_render_summary_template_backward_compatibility():
    """Test that templates without AI blocks still render correctly."""
    patient = PatientFactory.create(first_name="Alice", last_name="Smith")
    submission = FormSubmission.objects.create(
        patient=patient,
        status=FormSubmissionStatus.COMPLETED,
        data={"temperature": "98.6", "blood_pressure": "120/80"},
    )

    # Traditional template without AI blocks
    template_text = """# Medical Summary

**Patient:** {{ patient.first_name }} {{ patient.last_name }}

**Vitals:**
- Temperature: {{ submission.data.temperature }}°F
- Blood Pressure: {{ submission.data.blood_pressure }}
"""

    template = SummaryTemplateFactory.create(text=template_text)
    result = render_summary_template(template, submission)

    # Verify traditional rendering still works
    assert "Medical Summary" in result
    assert "Alice Smith" in result  # Patient name appears in rendered output
    assert "98.6" in result
    assert "120/80" in result
    assert "<h1>" in result  # Markdown was converted to HTML


@pytest.mark.vcr
@pytest.mark.django_db
def test_render_summary_template_multiple_ai_blocks():
    """Test rendering template with multiple AI blocks using real LLM (via VCR)."""
    patient = PatientFactory.create()
    submission = FormSubmission.objects.create(
        patient=patient,
        status=FormSubmissionStatus.COMPLETED,
        data={
            "history": "Diabetes, Hypertension",
            "medications": "Metformin, Lisinopril",
            "visit_reason": "Annual checkup",
        },
    )

    template_text = """# Annual Visit Summary

{% ai "Medical History Summary" %}
Summarize medical history: {{ submission.data.history }}
{% endai %}

{% ai "Medication Review" %}
Review medications: {{ submission.data.medications }}
{% endai %}

{% ai "Visit Assessment" %}
Assess visit: {{ submission.data.visit_reason }}
{% endai %}
"""

    template = SummaryTemplateFactory.create(text=template_text)
    result = render_summary_template(template, submission)

    # Verify all AI sections generated content (markdown converted to HTML)
    assert "<h1>Annual Visit Summary</h1>" in result
    # Should have substantial content from all three AI blocks
    assert len(result) > 200


@pytest.mark.vcr
@pytest.mark.django_db
def test_render_summary_template_empty_ai_response():
    """Test handling when AI receives minimal input using real LLM (via VCR)."""
    patient = PatientFactory.create()
    submission = FormSubmission.objects.create(
        patient=patient,
        status=FormSubmissionStatus.COMPLETED,
        data={},
    )

    template_text = """{% ai "Summary" %}Generate summary for empty patient data{% endai %}"""
    template = SummaryTemplateFactory.create(text=template_text)
    result = render_summary_template(template, submission)

    # Should handle empty data gracefully and still generate something
    assert result is not None
    assert len(result) > 0


@pytest.mark.vcr
@pytest.mark.django_db(transaction=True)
def test_generate_summary_task_with_ai_template(mock_job_context):
    """Test full summary generation flow with AI template using real LLM (via VCR)."""
    template = SummaryTemplateFactory.create(
        text="""# AI-Enhanced Summary

Patient: {{ patient.first_name }}

{% ai "Clinical Notes" %}
Generate notes for patient with symptoms: fatigue
{% endai %}
""",
        name="AI Summary",
    )

    patient = PatientFactory.create(
        first_name="Bob",
        organization=template.organization,
    )
    submission = FormSubmission.objects.create(
        patient=patient,
        status=FormSubmissionStatus.COMPLETED,
        data={"symptoms": "fatigue"},
    )
    summary = SummaryFactory.create(
        patient=patient,
        organization=template.organization,
        submission=submission,
        template=template,
        status=SummaryStatus.PENDING,
    )

    generate_summary_task(mock_job_context, summary_id=str(summary.id))

    summary.refresh_from_db()
    assert summary.status == SummaryStatus.SUCCEEDED
    assert summary.title == "AI Summary"
    assert "Patient: Bob" in summary.body
    # Should have generated clinical notes content
    assert len(summary.body) > len("# AI-Enhanced Summary\n\nPatient: Bob")


@pytest.mark.django_db(transaction=True)
def test_generate_summary_task_with_ai_template_llm_failure(mock_job_context):
    """Test that summary generation completes even when LLM fails.

    Note: This test doesn't use VCR because it's testing error handling,
    not actual LLM responses.
    """
    template = SummaryTemplateFactory.create(
        text="""{% ai "Summary" %}Generate summary{% endai %}""",
    )

    patient = PatientFactory.create(organization=template.organization)
    submission = FormSubmission.objects.create(
        patient=patient,
        status=FormSubmissionStatus.COMPLETED,
        data={},
    )
    summary = SummaryFactory.create(
        patient=patient,
        organization=template.organization,
        submission=submission,
        template=template,
        status=SummaryStatus.PENDING,
    )

    # This test relies on error handling in the actual code path
    generate_summary_task(mock_job_context, summary_id=str(summary.id))

    summary.refresh_from_db()
    # Summary should complete (either with LLM response or fallback)
    assert summary.status == SummaryStatus.SUCCEEDED
    assert summary.body is not None
    assert len(summary.body) > 0


# ============================================================================
# E2E Tests (using Playwright for browser testing)
# ============================================================================


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
def test_ai_summary_generation_e2e(live_server, page: Page, organization, provider, auth_provider_cookies):
    """
    End-to-end test of AI-enhanced summary generation flow.

    Tests: form submission -> AI summary generation -> summary display
    """
    # Setup: Use the organization from fixture (which provider has access to)
    patient = PatientFactory.create(organization=organization)
    form = FormFactory.create(organization=organization)

    # Create a summary template with AI blocks
    template = SummaryTemplateFactory.create(
        organization=organization,
        form=form,
        name="AI-Enhanced Clinical Summary",
        text="""# Clinical Summary for {{ patient.first_name }} {{ patient.last_name }}

**Patient Information:**
- Date of Birth: {{ patient.date_of_birth|date:"Y-m-d" }}
- Submission Date: {{ submission.submitted_at|date:"Y-m-d H:i" }}

{% ai "Clinical Assessment" %}
Based on the following patient data, provide a clinical assessment:

Chief Complaint: {{ submission.data.chief_complaint }}
Pain Scale: {{ submission.data.pain_scale }}/10
Symptoms: {{ submission.data.symptoms }}
Duration: {{ submission.data.duration }}

Provide a brief clinical assessment of the patient's condition.
{% endai %}

{% ai "Recommended Next Steps" %}
Based on the assessment, recommend appropriate next steps for:
- Further evaluation
- Treatment options
- Follow-up care
{% endai %}
""",
    )

    # Create a task and submission
    task = TaskFactory.create(
        form_version=form.get_current_version(),
        patient=patient,
    )

    submission = FormSubmission.objects.create(
        task=task,
        patient=patient,
        status=FormSubmissionStatus.COMPLETED,
        data={
            "chief_complaint": "Severe migraine headache",
            "pain_scale": "9",
            "symptoms": "nausea, photophobia, phonophobia",
            "duration": "2 days",
        },
    )

    # Create a pending summary
    summary = Summary.objects.create(
        patient=patient,
        organization=organization,
        template=template,
        submission=submission,
        title=template.name,
        body="",
        status=SummaryStatus.PENDING,
    )

    # Mock AI responses for predictable testing
    mock_ai_responses = {
        "Clinical Assessment": """## Clinical Assessment

The patient presents with severe migraine symptoms including:
- Intense headache (9/10 pain scale)
- Classic migraine symptoms: nausea, light and sound sensitivity
- 48-hour duration without relief

This presentation is consistent with acute migraine episode requiring intervention.""",
        "Recommended Next Steps": """## Recommended Next Steps

**Immediate Care:**
- Consider triptan medication if no contraindications
- Provide anti-nausea medication
- Recommend rest in dark, quiet environment

**Follow-up:**
- Schedule follow-up visit in 1 week
- Consider preventive migraine therapy if episodes are frequent
- Maintain headache diary to identify triggers""",
    }

    # Mock the AI summary service to avoid actual LLM calls
    with patch("sandwich.core.service.ai_template.batch_generate_summaries", return_value=mock_ai_responses):
        # Simulate summary generation (would normally be async via procrastinate)
        mock_context = type("Context", (), {"job": type("Job", (), {"id": 1, "task_name": "test"})()})()
        generate_summary_task(mock_context, summary_id=str(summary.id))

    summary.refresh_from_db()

    # Navigate to summary detail page
    summary_url = get_summary_url(summary)

    page.goto(f"{live_server.url}{summary_url}")
    page.wait_for_load_state("networkidle")

    # Verify summary metadata is displayed (patient name should appear somewhere on page)
    expect(page.get_by_text(patient.first_name).first).to_be_visible()
    expect(page.get_by_text(patient.last_name).first).to_be_visible()
    expect(page.get_by_text(template.name).first).to_be_visible()

    # Verify summary content is rendered
    expect(page.get_by_text("Clinical Assessment")).to_be_visible()
    expect(page.get_by_text("Recommended Next Steps")).to_be_visible()

    # Verify AI-generated content appears
    expect(page.locator("text=severe migraine symptoms")).to_be_visible()
    expect(page.locator("text=triptan medication")).to_be_visible()
    expect(page.locator("text=headache diary")).to_be_visible()

    # Verify status badge shows success
    expect(page.locator(".badge-success")).to_be_visible()


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
def test_ai_summary_loading_state_e2e(live_server, page: Page, organization, provider, auth_provider_cookies):
    """Test that processing summaries show loading indicator."""
    patient = PatientFactory.create(organization=organization)
    form = FormFactory.create(organization=organization)
    template = SummaryTemplateFactory.create(
        organization=organization,
        form=form,
        name="Processing Summary",
        text="{% ai 'Test' %}Test{% endai %}",
    )

    task = TaskFactory.create(
        form_version=form.get_current_version(),
        patient=patient,
    )
    submission = FormSubmission.objects.create(
        task=task,
        patient=patient,
        status=FormSubmissionStatus.COMPLETED,
        data={},
    )

    # Create summary in PROCESSING state
    summary = Summary.objects.create(
        patient=patient,
        organization=organization,
        template=template,
        submission=submission,
        title=template.name,
        body="",
        status=SummaryStatus.PROCESSING,
    )

    summary_url = get_summary_url(summary)

    # Navigate to summary detail page - clear any previous page state
    page.goto("about:blank")
    page.goto(f"{live_server.url}{summary_url}")
    page.wait_for_load_state("networkidle")

    # Verify processing state is displayed via the status badge
    expect(page.get_by_text("Processing").first).to_be_visible()

    # Verify status badge shows processing
    expect(page.locator(".badge-warning").first).to_be_visible()


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
def test_ai_summary_error_state_e2e(live_server, page: Page, organization, provider, auth_provider_cookies):
    """Test that failed summaries show error message."""
    patient = PatientFactory.create(organization=organization)
    form = FormFactory.create(organization=organization)
    template = SummaryTemplateFactory.create(
        organization=organization,
        form=form,
        name="Failed Summary",
        text="Test template",
    )

    task = TaskFactory.create(
        form_version=form.get_current_version(),
        patient=patient,
    )
    submission = FormSubmission.objects.create(
        task=task,
        patient=patient,
        status=FormSubmissionStatus.COMPLETED,
        data={},
    )

    # Create summary in FAILED state
    summary = Summary.objects.create(
        patient=patient,
        organization=organization,
        template=template,
        submission=submission,
        title=template.name,
        body="",
        status=SummaryStatus.FAILED,
    )

    summary_url = get_summary_url(summary)

    page.goto(f"{live_server.url}{summary_url}")
    page.wait_for_load_state("networkidle")

    # Verify failed status is displayed via the status badge
    expect(page.get_by_text("Failed").first).to_be_visible()

    # Verify status badge shows failed
    expect(page.locator(".badge-error")).to_be_visible()


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
def test_traditional_summary_without_ai_e2e(live_server, page: Page, organization, provider, auth_provider_cookies):
    """Test that traditional summaries (without AI blocks) still work correctly."""
    patient = PatientFactory.create(
        first_name="Jane",
        last_name="Doe",
        organization=organization,
    )
    form = FormFactory.create(organization=organization)

    # Template without AI blocks
    template = SummaryTemplateFactory.create(
        organization=organization,
        form=form,
        name="Traditional Summary",
        text="""# Summary for {{ patient.first_name }} {{ patient.last_name }}

**Chief Complaint:** {{ submission.data.complaint }}

**Assessment:** Basic assessment text.
""",
    )

    task = TaskFactory.create(
        form_version=form.get_current_version(),
        patient=patient,
    )
    submission = FormSubmission.objects.create(
        task=task,
        patient=patient,
        status=FormSubmissionStatus.COMPLETED,
        data={"complaint": "Annual checkup"},
    )

    summary = Summary.objects.create(
        patient=patient,
        organization=organization,
        template=template,
        submission=submission,
        title=template.name,
        body="",
        status=SummaryStatus.PENDING,
    )

    # Generate summary (should use traditional rendering path)
    mock_context = type("Context", (), {"job": type("Job", (), {"id": 1, "task_name": "test"})()})()
    generate_summary_task(mock_context, summary_id=str(summary.id))

    summary.refresh_from_db()

    summary_url = get_summary_url(summary)

    page.goto(f"{live_server.url}{summary_url}")
    page.wait_for_load_state("networkidle")

    # Verify traditional content is rendered
    expect(page.get_by_text("Summary for Jane Doe")).to_be_visible()
    expect(page.get_by_text("Annual checkup")).to_be_visible()
    expect(page.get_by_text("Basic assessment text")).to_be_visible()
    expect(page.locator(".badge-success")).to_be_visible()
