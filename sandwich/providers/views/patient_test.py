import pytest
from django.test import Client
from django.urls import reverse

from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.organization import Organization
from sandwich.core.models.patient import Patient
from sandwich.core.service.encounter_service import assign_default_encounter_perms
from sandwich.core.service.patient_service import assign_default_provider_patient_permissions
from sandwich.users.models import User


@pytest.mark.django_db
def test_patient_list(provider: User, organization: Organization) -> None:
    client = Client()
    client.force_login(provider)
    res = client.post(
        reverse(
            "providers:patient_list",
            kwargs={
                "organization_id": organization.id,
            },
        )
    )

    assert res.status_code == 200


@pytest.mark.django_db
def test_patient_add(provider: User, organization: Organization) -> None:
    client = Client()
    client.force_login(provider)
    res = client.post(
        reverse(
            "providers:patient_add",
            kwargs={
                "organization_id": organization.id,
            },
        )
    )

    assert res.status_code == 200


@pytest.mark.django_db
def test_patient_add_deny_access(user: User, organization: Organization, patient: Patient) -> None:
    client = Client()
    client.force_login(user)
    res = client.post(
        reverse(
            "providers:patient_add",
            kwargs={
                "organization_id": organization.id,
            },
        )
    )

    assert res.status_code == 403


# TODO(MM): Backfill with Task perm tests
@pytest.mark.django_db
def test_patient_add_task(provider: User, organization: Organization, patient: Patient) -> None:
    client = Client()
    client.force_login(provider)
    assign_default_provider_patient_permissions(patient)
    res = client.post(
        reverse("providers:patient_add_task", kwargs={"organization_id": organization.id, "patient_id": patient.id})
    )

    assert res.status_code == 302
    assert res.url == reverse(  # type:ignore [attr-defined]
        "providers:patient", kwargs={"organization_id": organization.id, "patient_id": patient.id}
    )


@pytest.mark.django_db
def test_patient_add_task_deny_access(user: User, organization: Organization, patient: Patient) -> None:
    client = Client()
    client.force_login(user)
    res = client.post(
        reverse("providers:patient_add_task", kwargs={"organization_id": organization.id, "patient_id": patient.id})
    )

    assert res.status_code == 403


@pytest.mark.django_db
def test_patient_archive(provider: User, organization: Organization, patient: Patient) -> None:
    client = Client()
    client.force_login(provider)
    encounter = Encounter.objects.create(
        organization=organization, patient=patient, status=EncounterStatus.IN_PROGRESS
    )
    assign_default_encounter_perms(encounter)

    res = client.post(
        reverse("providers:patient_archive", kwargs={"organization_id": organization.id, "patient_id": patient.id})
    )

    assert res.status_code == 302
    assert res.url == reverse("providers:patient_list", kwargs={"organization_id": organization.id})  # type:ignore [attr-defined]
