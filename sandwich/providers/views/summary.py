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
    """Display a standalone summary detail page."""
    logger.info(
        "Accessing summary detail",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "summary_id": summary.id,
            "patient_id": summary.patient.id,
        },
    )

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

    context = {
        "organization": organization,
        "summary": summary,
        "patient": summary.patient,
        "encounter": summary.encounter,
        "breadcrumb_url": breadcrumb_url,
        "breadcrumb_text": breadcrumb_text,
    }

    return render(request, "provider/summary_detail.html", context)
