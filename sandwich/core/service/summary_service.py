"""Service for generating summaries from templates and form submissions."""

import logging
from typing import TYPE_CHECKING

from django.template import Context
from django.template import Template
from guardian.shortcuts import assign_perm

from sandwich.core.models.role import RoleName
from sandwich.core.models.summary import Summary
from sandwich.core.models.summary import SummaryStatus
from sandwich.core.models.summary_template import SummaryTemplate
from sandwich.core.service.markdown_service import markdown_to_html
from sandwich.core.types import HtmlStr
from sandwich.core.util.procrastinate import define_task

if TYPE_CHECKING:
    from sandwich.core.models.form_submission import FormSubmission

logger = logging.getLogger(__name__)


def assign_default_summary_perms(summary: Summary) -> None:
    """Assign default permissions for a summary to organization roles and patient user."""
    if summary.organization:
        for role_name in [RoleName.OWNER, RoleName.ADMIN, RoleName.STAFF]:
            role = summary.organization.get_role(role_name)
            assign_perm("view_summary", role.group, summary)
        logger.info(
            "Providers from org have been given summary permissions",
            extra={
                "organization_id": summary.organization.id,
                "patient_id": summary.patient.id,
                "summary_id": summary.id,
            },
        )
    else:
        logger.info(
            "Summary has no organization for permissions",
            extra={
                "patient_id": summary.patient.id,
                "summary_id": summary.id,
            },
        )
    if summary.patient.user:
        assign_perm("view_summary", summary.patient.user, summary)
        logger.info(
            "Patient has been given summary permissions",
            extra={
                "patient_id": summary.patient.id,
                "summary_id": summary.id,
            },
        )
    else:
        logger.info(
            "Patient has no associated user for summary permissions",
            extra={
                "patient_id": summary.patient.id,
                "summary_id": summary.id,
            },
        )


@define_task
def generate_summary_task(summary_id: str) -> None:
    try:
        summary = Summary.objects.select_related(
            "template", "submission", "submission__patient", "submission__task"
        ).get(id=summary_id)
    except Summary.DoesNotExist:
        logger.exception(
            "Summary not found for generation",
            extra={"summary_id": str(summary_id)},
        )
        return

    updated = Summary.objects.filter(id=summary_id, status=SummaryStatus.PENDING).update(
        status=SummaryStatus.PROCESSING
    )

    if not updated:
        logger.info(
            "Summary already being processed or not in pending state",
            extra={"summary_id": str(summary_id), "current_status": summary.status},
        )
        return

    logger.info(
        "Starting summary generation",
        extra={
            "summary_id": str(summary_id),
            "patient_id": str(summary.patient_id),
            "template_id": str(summary.template_id) if summary.template_id else None,
        },
    )

    if not summary.template:
        logger.error("Summary has no template", extra={"summary_id": str(summary_id)})
        Summary.objects.filter(id=summary_id).update(status=SummaryStatus.FAILED)
        return

    try:
        rendered_body = render_summary_template(
            template=summary.template,
            submission=summary.submission,
        )

        Summary.objects.filter(id=summary_id).update(
            title=summary.template.name,
            body=rendered_body,
            status=SummaryStatus.SUCCEEDED,
        )

        logger.info(
            "Summary generation completed successfully",
            extra={
                "summary_id": str(summary_id),
                "patient_id": str(summary.patient_id),
            },
        )
    except Exception:
        logger.exception(
            "Unexpected error generating summary",
            extra={"summary_id": str(summary_id)},
        )
        Summary.objects.filter(id=summary_id).update(status=SummaryStatus.FAILED)


def trigger_summary_generation(submission: "FormSubmission") -> None:
    if not submission.task or not submission.task.form_version:
        return

    if not submission.patient.organization:
        logger.warning(
            "Cannot generate summary for patient without organization",
            extra={"patient_id": str(submission.patient_id), "submission_id": str(submission.id)},
        )
        return

    form = submission.task.form_version.pgh_obj

    templates = SummaryTemplate.objects.filter(
        form=form,
        organization=submission.patient.organization,
    )

    for template in templates:
        summary = Summary.objects.create(
            patient=submission.patient,
            organization=submission.patient.organization,
            encounter=submission.task.encounter if submission.task else None,
            template=template,
            submission=submission,
            title=template.name,
            body="",
            status=SummaryStatus.PENDING,
        )

        generate_summary_task.defer(summary_id=str(summary.id))

        logger.info(
            "Queued summary generation",
            extra={
                "summary_id": str(summary.id),
                "template_id": str(template.id),
                "submission_id": str(submission.id),
                "patient_id": str(submission.patient_id),
            },
        )


def render_summary_template(
    template: "SummaryTemplate",
    submission: "FormSubmission",
) -> HtmlStr:
    """Render a summary template with form submission data."""
    context = {
        "patient": submission.patient,
        "submission": submission,
    }

    django_template = Template(template.text)
    django_context = Context(context)

    markdown_text = django_template.render(django_context)

    return markdown_to_html(markdown_text, preset="commonmark")
