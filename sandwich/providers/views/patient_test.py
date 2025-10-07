from http import HTTPStatus
from typing import TYPE_CHECKING
from typing import cast

from django.test import Client
from django.urls import URLPattern
from django.urls import URLResolver
from django.urls import reverse

from sandwich.core.factories import PatientFactory
from sandwich.core.models import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.role import RoleName
from sandwich.core.service.organization_service import assign_organization_role
from sandwich.core.urls_test import get_all_urls
from sandwich.providers.urls import urlpatterns as providers_urlpatterns

if TYPE_CHECKING:
    from sandwich.core.models import Patient


def get_provider_urls() -> list[URLPattern | URLResolver]:
    return get_all_urls(providers_urlpatterns)  # type: ignore[arg-type]


def test_provider_http_get_urls_return_status_200(db, user, organization) -> None:
    # Setup a provider-like user.
    assign_organization_role(organization, RoleName.OWNER, user)
    client = Client()
    client.force_login(user)

    # Need a patient in the org with an encounter
    patient = cast("Patient", PatientFactory(organization=organization))
    encounter = Encounter.objects.create(
        patient=patient, organization=organization, status=EncounterStatus.IN_PROGRESS
    )

    # List of urls which are other http verbs (e.g. POST) or redirect (non HTTP 200)
    exclude_url_names = [
        "home",  # Redirect
        "organization",  # Redirect
        "patient_archive",  # POST
        "patient_add_task",  # POST
        "patient_resend_invite",  # POST
        "patient_cancel_task",  # POST
    ]

    # Get registered provider URLs
    provider_urls = get_provider_urls()
    found_provider_route_names = {
        obj.get("name")  # type: ignore[union-attr]
        for obj in provider_urls
        if obj.get("name") and obj.get("name") not in exclude_url_names  # type: ignore[union-attr]
    }

    urls = [
        (reverse("providers:organization_add"), "organization_add"),
        (reverse("providers:organization_edit", kwargs={"organization_id": organization.id}), "organization_edit"),
        (reverse("providers:search", kwargs={"organization_id": organization.id}), "search"),
        (reverse("providers:encounter_list", kwargs={"organization_id": organization.id}), "encounter_list"),
        (
            reverse("providers:encounter", kwargs={"organization_id": organization.id, "encounter_id": encounter.id}),
            "encounter",
        ),
        (
            reverse("providers:patient", kwargs={"organization_id": organization.id, "patient_id": patient.id}),
            "patient",
        ),
        (
            reverse("providers:patient_edit", kwargs={"organization_id": organization.id, "patient_id": patient.id}),
            "patient_edit",
        ),
        (reverse("providers:patient_list", kwargs={"organization_id": organization.id}), "patient_list"),
        (reverse("providers:patient_add", kwargs={"organization_id": organization.id}), "patient_add"),
    ]
    tested_provider_route_names = set()
    for url, url_name in urls:
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK, f"URL {url_name} returned {response.status_code}"
        tested_provider_route_names.add(url_name)

    assert found_provider_route_names == tested_provider_route_names
