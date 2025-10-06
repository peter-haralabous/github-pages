from http import HTTPStatus
from typing import TYPE_CHECKING
from typing import cast

from django.test import Client
from django.urls import reverse

from sandwich.core.factories import PatientFactory
from sandwich.core.models import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.role import RoleName
from sandwich.core.service.organization_service import assign_organization_role

if TYPE_CHECKING:
    from sandwich.core.models import Patient


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

    urls = [
        # Redirects
        #  - providers:home
        #  - providers:organization
        reverse("providers:organization_add"),
        reverse("providers:organization_edit", kwargs={"organization_id": organization.id}),
        reverse("providers:search", kwargs={"organization_id": organization.id}),
        reverse("providers:encounter_list", kwargs={"organization_id": organization.id}),
        reverse("providers:encounter", kwargs={"organization_id": organization.id, "encounter_id": encounter.id}),
        reverse("providers:patient", kwargs={"organization_id": organization.id, "patient_id": patient.id}),
        reverse("providers:patient_edit", kwargs={"organization_id": organization.id, "patient_id": patient.id}),
        # HTTP POST only
        #  - providers:patient_archive
        #  - providers:patient_add_task
        #  - providers:patient_resent_invite
        #  - providers:patient_cancel_task
        reverse("providers:patient_list", kwargs={"organization_id": organization.id}),
        reverse("providers:patient_add", kwargs={"organization_id": organization.id}),
    ]
    assert urls is not None, "No URLs to test"
    for url in urls:
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK, f"URL {url} returned {response.status_code}"
