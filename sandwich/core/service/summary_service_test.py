"""Tests for summary service."""

import uuid
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from django.utils import timezone

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
    context = MagicMock()
    context.job.id = 1
    context.job.task_name = "generate_summary_task"
    return context


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
