import logging
from dataclasses import dataclass

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse

from sandwich.core.models.organization import Organization
from sandwich.core.models.patient import Patient
from sandwich.core.service.patient_service import maybe_patient_name
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


@dataclass
class Result:
    name: str
    url: str


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization"])])
def search(request: AuthenticatedHttpRequest, organization: Organization):
    logger.info("Starting patient search", extra={"organization_id": organization.id, "user_id": request.user.id})

    q = request.GET.get("q", "").strip()

    logger.debug(
        "Search query received",
        extra={"organization_id": organization.id, "query_length": len(q), "has_query": bool(q)},
    )

    # TODO: sort these sensibly
    results: list[Result] = []

    if q:
        patients = Patient.objects.filter(organization=organization).search(q)[:20]  # type: ignore[attr-defined]

        logger.debug(
            "Patient search completed", extra={"organization_id": organization.id, "results_count": len(patients)}
        )

        results.extend(
            Result(
                name=f"{p.full_name}",
                url=reverse("providers:patient", kwargs={"organization_id": organization.id, "patient_id": p.id}),
            )
            for p in patients
        )

    # TODO: extend this to handle email addresses, etc.
    if maybe_name := maybe_patient_name(q):
        results.append(
            Result(
                name=f'Create patient "{" ".join(maybe_name).strip()}"',
                # TODO-NG: pass maybe_name through to patient_add
                url=reverse(
                    "providers:patient_add", kwargs={"organization_id": organization.id}, query={"maybe_name": q}
                ),
            )
        )
        logger.debug("Added create patient option with parsed name", extra={"organization_id": organization.id})
    else:
        results.append(
            Result(
                name="Create a new patient",
                url=reverse("providers:patient_add", kwargs={"organization_id": organization.id}),
            )
        )
        logger.debug("Added generic create patient option", extra={"organization_id": organization.id})

    logger.info("Search completed", extra={"organization_id": organization.id, "total_results": len(results)})

    context = {"results": results}
    return render(request, "provider/partials/search_results.html", context)
