import logging
from dataclasses import dataclass

from django.contrib.auth.decorators import login_required
from django.db.models import OuterRef
from django.db.models import Q
from django.db.models import Subquery
from django.shortcuts import render
from django.urls import reverse

from sandwich.core.models.encounter import ACTIVE_ENCOUNTER_STATUSES
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.organization import Organization
from sandwich.core.models.patient import Patient
from sandwich.core.service.patient_service import maybe_patient_name
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


@dataclass
class Result:
    icon: str
    title: str
    url: str
    patient: Patient | None = None
    encounter: Encounter | None = None


def _patient_search_results(organization: Organization, query: str) -> list[Result]:
    logger.debug(
        "Searching for patients",
        extra={"organization_id": organization.id, "query_length": len(query)},
    )

    # TODO: sort these sensibly
    #       ✅ encounters come first (my organization has already interacted with this patient)
    #       ✅ active encounters come before inactive ones
    results: list[Result] = []
    if query:
        encounter_query = (
            Encounter.objects.filter(organization=organization)
            .search(query)  # type: ignore[attr-defined]
            .annotate(is_active=Q(status__in=ACTIVE_ENCOUNTER_STATUSES))
            .order_by("-is_active")
        )
        # get only the top encounter per patient
        # if there's an active and an archived encounter for the same patient, we should only show the active one
        # if there are only archived encounters, then the expected flow is for the user to create a new one
        # so it doesn't matter too much which one we show here
        # TODO: if there's more than one active, show both?
        encounter_ids = encounter_query.filter(patient_id=OuterRef("patient_id")).values("id")[:1]
        encounters = (Encounter.objects.filter(id__in=Subquery(encounter_ids)).select_related("patient"))[:20]

        patients = (
            Patient.objects.filter(organization=organization)
            .search(query)  # type: ignore[attr-defined]
            .exclude(id__in=[e.patient.id for e in encounters])
        )[:20]

        logger.debug(
            "Patient search completed",
            extra={
                "organization_id": organization.id,
                "patient_count": len(patients),
                "encounter_count": len(encounters),
            },
        )

        results.extend(
            Result(
                icon="clipboard-list" if e.active else "archive",
                title=f"{e.patient.full_name}",
                url=reverse("providers:encounter", kwargs={"organization_id": organization.id, "encounter_id": e.id}),
                patient=e.patient,
                encounter=e,
            )
            for e in encounters
        )

        results.extend(
            Result(
                icon="user-search",
                title=f"{p.full_name}",
                url=reverse("providers:patient", kwargs={"organization_id": organization.id, "patient_id": p.id}),
                patient=p,
            )
            for p in patients
        )

    logger.info("Search completed", extra={"organization_id": organization.id, "total_results": len(results)})
    return results


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization"])])
def search(request: AuthenticatedHttpRequest, organization: Organization):
    logger.info("Starting patient search", extra={"organization_id": organization.id, "user_id": request.user.id})

    q = request.GET.get("q", "").strip()

    results = _patient_search_results(organization, q)

    # TODO: extend this to handle email addresses, etc.
    # do actions always come after patients, or can I search for "Add Patient"?
    if maybe_name := maybe_patient_name(q):
        results.append(
            Result(
                icon="user-plus",
                title=f'Create patient "{" ".join(maybe_name).strip()}"',
                url=reverse(
                    "providers:patient_add", kwargs={"organization_id": organization.id}, query={"maybe_name": q}
                ),
            )
        )
    else:
        results.append(
            Result(
                icon="user-plus",
                title="Create a new patient",
                url=reverse("providers:patient_add", kwargs={"organization_id": organization.id}),
            )
        )

    context = {"results": results}
    return render(request, "provider/partials/search_results.html", context)
