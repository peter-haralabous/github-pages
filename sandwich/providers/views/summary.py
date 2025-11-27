import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse

from sandwich.core.models.organization import Organization
from sandwich.core.models.summary import Summary
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


@login_required
@authorize_objects(
    [
        ObjPerm(Organization, "organization_id", ["view_organization"]),
        ObjPerm(Summary, "summary_id", ["view_summary"]),
    ]
)
def summary_detail(request: AuthenticatedHttpRequest, organization: Organization, summary: Summary) -> HttpResponse:
    """Display summary detail - returns modal for HTMX requests, full page otherwise."""
    is_htmx = bool(request.headers.get("HX-Request"))
    is_print = request.GET.get("print") == "true"

    logger.info(
        "Accessing summary detail",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "summary_id": summary.id,
            "patient_id": summary.patient.id,
            "is_htmx": is_htmx,
            "is_print": is_print,
        },
    )

    context = {
        "organization": organization,
        "summary": summary,
        "patient": summary.patient,
        "encounter": summary.encounter,
    }

    # If print request, return print template
    if is_print:
        return render(request, "provider/summary_detail_print.html", context)

    # If HTMX request, return modal partial
    if is_htmx:
        return render(request, "provider/partials/summary_modal.html", context)

    # Otherwise return full page with breadcrumbs
    if summary.encounter:
        breadcrumb_url = reverse(
            "providers:encounter",
            kwargs={"organization_id": organization.id, "encounter_id": summary.encounter.id},
        )
        breadcrumb_text = "Back to encounter"
    else:
        breadcrumb_url = reverse(
            "providers:patient",
            kwargs={"organization_id": organization.id, "patient_id": summary.patient.id},
        )
        breadcrumb_text = "Back to patient"

    context["breadcrumb_url"] = breadcrumb_url  # type: ignore[assignment]
    context["breadcrumb_text"] = breadcrumb_text  # type: ignore[assignment]

    return render(request, "provider/summary_detail.html", context)
