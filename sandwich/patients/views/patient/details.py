import logging
from typing import Any

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.timezone import now
from django.views.decorators.http import require_POST

from sandwich.core.models import Patient
from sandwich.core.models.task import ACTIVE_TASK_STATUSES
from sandwich.core.service.health_record_service import get_total_health_record_count
from sandwich.core.service.health_summary_service import generate_health_summary
from sandwich.core.service.markdown_service import markdown_to_html
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.patients.views.patient import _chat_context

logger = logging.getLogger(__name__)


def _chatty_patient_details_context(request: AuthenticatedHttpRequest, patient: Patient) -> dict[str, Any]:
    records_count = get_total_health_record_count(patient)
    repository_count = patient.document_set.count()
    tasks_count = patient.task_set.filter(status__in=ACTIVE_TASK_STATUSES).count()

    # Try to retrieve cached health summary
    cache_key = f"health_summary:{patient.id}"
    cached_summary = cache.get(cache_key)

    if cached_summary:
        return {
            "records_count": records_count,
            "repository_count": repository_count,
            "tasks_count": tasks_count,
            "health_summary_html": cached_summary["html"],
            "health_summary_generated_at": cached_summary["generated_at"],
        } | _chat_context(request, patient=patient)

    # Health summary is not auto-generated - only generated on manual refresh
    return {
        "records_count": records_count,
        "repository_count": repository_count,
        "tasks_count": tasks_count,
        "health_summary_html": None,
        "health_summary_generated_at": None,
    } | _chat_context(request, patient=patient)


@login_required
@authorize_objects([ObjPerm(Patient, "patient_id", ["view_patient"])])
def patient_details(request: AuthenticatedHttpRequest, patient: Patient) -> HttpResponse:
    template = "patient/chatty/app.html"
    context = _chatty_patient_details_context(request, patient)

    if request.headers.get("HX-Target") == "left-panel":
        template = "patient/chatty/partials/left_panel.html"

    return render(request, template, context)


@login_required
@authorize_objects([ObjPerm(Patient, "patient_id", ["view_patient"])])
@require_POST
def regenerate_health_summary(request: AuthenticatedHttpRequest, patient: Patient) -> HttpResponse:
    """Regenerate the health summary and return the updated right panel."""
    context = _chatty_patient_details_context(request, patient)

    # Generate health summary on-demand
    try:
        health_summary = generate_health_summary(patient)
        health_summary_html = markdown_to_html(health_summary)
        logger.info(
            "Health summary generated on-demand",
            extra={
                "patient_id": str(patient.id),
                "has_html": health_summary_html is not None,
                "html_length": len(health_summary_html) if health_summary_html else 0,
            },
        )

        # Cache the generated summary for 24 hours
        cache_key = f"health_summary:{patient.id}"
        cache.set(
            cache_key,
            {"html": health_summary_html, "generated_at": now()},
            timeout=60 * 60 * 24,  # 24 hours
        )
    except Exception:
        logger.exception("Failed to generate health summary")
        health_summary_html = None

    # Update context with generated summary
    context.update({"health_summary_html": health_summary_html})

    return render(request, "patient/chatty/partials/right_panel.html", context)
