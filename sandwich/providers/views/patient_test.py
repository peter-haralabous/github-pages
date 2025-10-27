from datetime import date

import pytest
from django.test import Client
from django.urls import reverse
from guardian.shortcuts import assign_perm

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.organization import Organization
from sandwich.core.models.patient import Patient
from sandwich.core.models.role import RoleName
from sandwich.core.service.encounter_service import assign_default_encounter_perms
from sandwich.core.service.organization_service import assign_organization_role
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
def test_patient_list_filter_allowed_patients(provider: User, organization: Organization) -> None:
    # Create org patients
    PatientFactory.create(organization=organization)
    PatientFactory.create(organization=organization)
    # Unrelated patient
    PatientFactory.create()

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
    # We only get the patients the provider has permissions to view
    assert len(res.context["patients"]) == 2


@pytest.mark.django_db
def test_patient_add(provider: User, organization: Organization) -> None:
    assign_organization_role(organization=organization, role_name=RoleName.STAFF, user=provider)

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
def test_patient_add_deny_access_not_provider(user: User, organization: Organization) -> None:
    data = {
        "first_name": "Jacob",
        "last_name": "Newpatient",
        "date_of_birth": date(1961, 6, 6),
        "province": "BC",
        "phn": "9111111117",  # BC requires more specific PHN
    }

    client = Client()
    client.force_login(user)
    res = client.post(
        reverse(
            "providers:patient_add",
            kwargs={
                "organization_id": organization.id,
            },
        ),
        data=data,
    )

    assert res.status_code == 404


@pytest.mark.django_db
def test_patient_add_deny_access_missing_perms(user: User, organization: Organization) -> None:
    data = {
        "first_name": "Jacob",
        "last_name": "Newpatient",
        "date_of_birth": date(1961, 6, 6),
        "province": "BC",
        "phn": "9111111117",  # BC requires more specific PHN
    }

    # Has `create_encounter` but not `create_patient`
    assign_perm("create_encounter", user, organization)

    client = Client()
    client.force_login(user)
    res = client.post(
        reverse(
            "providers:patient_add",
            kwargs={
                "organization_id": organization.id,
            },
        ),
        data=data,
    )

    assert res.status_code == 404


@pytest.mark.django_db
def test_patient_details(provider: User, patient: Patient, organization: Organization) -> None:
    client = Client()
    client.force_login(provider)
    res = client.get(
        reverse(
            "providers:patient",
            kwargs={
                "patient_id": patient.id,
                "organization_id": organization.id,
            },
        )
    )

    assert res.status_code == 200


@pytest.mark.django_db
def test_patient_details_deny_access(provider: User, organization: Organization) -> None:
    other_patient = PatientFactory.create()
    client = Client()
    client.force_login(provider)
    res = client.get(
        reverse(
            "providers:patient",
            kwargs={
                "patient_id": other_patient.id,
                "organization_id": organization.id,
            },
        )
    )

    assert res.status_code == 404


@pytest.mark.django_db
def test_patient_edit(provider: User, patient: Patient, organization: Organization) -> None:
    data = {
        "first_name": "Jacob",
        "last_name": "Newname",
        "date_of_birth": date(1961, 6, 6),
        "province": "BC",
        "phn": "9111111117",  # BC requires more specific PHN
    }

    client = Client()
    client.force_login(provider)
    res = client.post(
        reverse(
            "providers:patient_edit",
            kwargs={
                "patient_id": patient.id,
                "organization_id": organization.id,
            },
        ),
        data=data,
    )

    assert res.status_code == 302
    assert res.url == reverse(  # type: ignore[attr-defined]
        "providers:patient",
        kwargs={"patient_id": patient.id, "organization_id": organization.id},
    )
    patient.refresh_from_db()
    assert patient.last_name == "Newname"


@pytest.mark.django_db
def test_patient_edit_deny_access(provider: User, patient: Patient, organization: Organization) -> None:
    other_patient = PatientFactory.create()
    data = {
        "first_name": "Jacob",
        "last_name": "Newname",
        "date_of_birth": date(1961, 6, 6),
        "province": "BC",
        "phn": "9111111117",  # BC requires more specific PHN
    }

    client = Client()
    client.force_login(provider)
    res = client.post(
        reverse(
            "providers:patient_edit",
            kwargs={
                "patient_id": other_patient.id,
                "organization_id": organization.id,
            },
        ),
        data=data,
    )

    assert res.status_code == 404


# TODO(MM): Backfill with Task perm tests
@pytest.mark.django_db
def test_patient_add_task(provider: User, organization: Organization, patient: Patient) -> None:
    client = Client()
    client.force_login(provider)
    assert patient.task_set.count() == 0
    res = client.post(
        reverse(
            "providers:patient_add_task",
            kwargs={"organization_id": organization.id, "patient_id": patient.id},
        )
    )
    assert patient.task_set.count() == 1
    task = patient.task_set.first()
    assert task is not None
    assert task.form_version is None  # No form associated yet. Formio still hardcoded in.

    assert res.status_code == 302
    assert res.url == reverse(  # type:ignore [attr-defined]
        "providers:patient",
        kwargs={"organization_id": organization.id, "patient_id": patient.id},
    )


@pytest.mark.django_db
def test_patient_add_task_deny_access(user: User, organization: Organization, patient: Patient) -> None:
    client = Client()
    client.force_login(user)
    res = client.post(
        reverse(
            "providers:patient_add_task",
            kwargs={"organization_id": organization.id, "patient_id": patient.id},
        )
    )

    assert res.status_code == 404


@pytest.mark.django_db
def test_patient_archive(provider: User, organization: Organization, patient: Patient) -> None:
    client = Client()
    client.force_login(provider)
    encounter = Encounter.objects.create(
        organization=organization, patient=patient, status=EncounterStatus.IN_PROGRESS
    )
    assign_default_encounter_perms(encounter)

    res = client.post(
        reverse(
            "providers:patient_archive",
            kwargs={"organization_id": organization.id, "patient_id": patient.id},
        )
    )

    assert res.status_code == 302
    assert res.url == reverse("providers:patient_list", kwargs={"organization_id": organization.id})  # type:ignore [attr-defined]


@pytest.mark.django_db
def test_patient_archive_deny_access(user: User, organization: Organization, patient: Patient) -> None:
    client = Client()
    # This user doesn't have change_encounter perms, only view
    client.force_login(user)
    encounter = Encounter.objects.create(
        organization=organization, patient=patient, status=EncounterStatus.IN_PROGRESS
    )
    assign_default_encounter_perms(encounter)

    res = client.post(
        reverse(
            "providers:patient_archive",
            kwargs={"organization_id": organization.id, "patient_id": patient.id},
        )
    )

    assert res.status_code == 404
