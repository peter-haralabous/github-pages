from typing import Any

from sandwich.core.factories.form import FormFactory
from sandwich.core.factories.form_submission import FormSubmissionFactory
from sandwich.core.factories.summary import SummaryFactory
from sandwich.core.factories.summary_template import SummaryTemplateFactory
from sandwich.core.models import Encounter
from sandwich.core.models import Organization
from sandwich.core.models import Patient
from sandwich.core.models import Summary
from sandwich.core.models import SummaryStatus


def test_create_summary_minimal(db: Any, patient: Patient, organization: Organization) -> None:
    form_submission = FormSubmissionFactory.create(patient=patient, task=None)
    summary = SummaryFactory.create(
        patient=patient,
        organization=organization,
        submission=form_submission,
        title="Test Summary",
    )

    assert summary.id is not None
    assert summary.status == SummaryStatus.PENDING
    assert summary.body == ""
    assert summary.encounter is None
    assert summary.template is None
    assert summary.submission == form_submission


def test_create_summary_full(db: Any, patient: Patient, organization: Organization, encounter: Encounter) -> None:
    form = FormFactory.create(organization=organization, name="Visit Form")
    template = SummaryTemplateFactory.create(
        organization=organization,
        form=form,
        name="Visit Note",
        text="# Template",
    )
    form_submission = FormSubmissionFactory.create(patient=patient, task=None)

    summary = SummaryFactory.create(
        patient=patient,
        organization=organization,
        encounter=encounter,
        template=template,
        submission=form_submission,
        title="Visit Note",
        body="# Summary content here",
        status=SummaryStatus.SUCCEEDED,
    )

    assert summary.encounter == encounter
    assert summary.template == template
    assert summary.submission == form_submission


def test_status_transitions(db: Any, patient: Patient, organization: Organization) -> None:
    form_submission = FormSubmissionFactory.create(patient=patient, task=None)
    summary = SummaryFactory.create(
        patient=patient,
        organization=organization,
        submission=form_submission,
        title="Test",
    )

    assert summary.status == SummaryStatus.PENDING
    assert not summary.is_complete

    summary.status = SummaryStatus.PROCESSING
    summary.save()
    assert not summary.is_complete

    summary.status = SummaryStatus.SUCCEEDED
    summary.body = "Generated content"
    summary.save()
    assert summary.is_complete


def test_template_deletion_sets_null(db: Any, patient: Patient, organization: Organization) -> None:
    form = FormFactory.create(organization=organization, name="Test Form")
    template = SummaryTemplateFactory.create(
        organization=organization,
        form=form,
        name="Test Template",
        text="# Template",
    )
    form_submission = FormSubmissionFactory.create(patient=patient, task=None)

    summary = SummaryFactory.create(
        patient=patient,
        organization=organization,
        template=template,
        submission=form_submission,
        title="Test",
    )

    template.delete()

    summary.refresh_from_db()
    assert summary.template is None
    assert summary.id is not None  # Summary still exists


def test_patient_deletion_cascades(db: Any, patient: Patient, organization: Organization) -> None:
    form_submission = FormSubmissionFactory.create(patient=patient, task=None)
    summary = SummaryFactory.create(
        patient=patient,
        organization=organization,
        submission=form_submission,
        title="Test",
    )

    summary_id = summary.id
    patient.delete()

    assert not Summary.objects.filter(id=summary_id).exists()


def test_organization_deletion_cascades(db: Any, patient: Patient, organization: Organization) -> None:
    form_submission = FormSubmissionFactory.create(patient=patient, task=None)
    summary = SummaryFactory.create(
        patient=patient,
        organization=organization,
        submission=form_submission,
        title="Test",
    )

    summary_id = summary.id
    organization.delete()

    assert not Summary.objects.filter(id=summary_id).exists()


def test_submission_deletion_cascades(db: Any, patient: Patient, organization: Organization) -> None:
    form_submission = FormSubmissionFactory.create(patient=patient, task=None)
    summary = SummaryFactory.create(
        patient=patient,
        organization=organization,
        submission=form_submission,
        title="Test",
    )

    summary_id = summary.id
    form_submission.delete()

    assert not Summary.objects.filter(id=summary_id).exists()


def test_str_representation(db: Any, patient: Patient, organization: Organization) -> None:
    form_submission = FormSubmissionFactory.create(patient=patient, task=None)
    summary = SummaryFactory.create(
        patient=patient,
        organization=organization,
        submission=form_submission,
        title="Visit Note",
        status=SummaryStatus.SUCCEEDED,
    )

    expected = f"Visit Note - {patient.full_name} (Succeeded)"
    assert str(summary) == expected


def test_summary_ordering(db: Any, patient: Patient, organization: Organization) -> None:
    form_submission1 = FormSubmissionFactory.create(patient=patient, task=None)
    form_submission2 = FormSubmissionFactory.create(patient=patient, task=None)

    summary1 = SummaryFactory.create(
        patient=patient,
        organization=organization,
        submission=form_submission1,
        title="First",
    )
    summary2 = SummaryFactory.create(
        patient=patient,
        organization=organization,
        submission=form_submission2,
        title="Second",
    )

    summaries = list(Summary.objects.filter(patient=patient))

    # Most recent first
    assert summaries[0] == summary2
    assert summaries[1] == summary1
