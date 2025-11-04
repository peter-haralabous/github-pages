from datetime import date
from http import HTTPStatus

from django.test import Client
from django.urls import reverse
from guardian.shortcuts import remove_perm

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.factories.task import TaskFactory
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.organization import Organization
from sandwich.core.models.patient import Patient
from sandwich.core.models.task import TaskStatus
from sandwich.users.models import User


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

    assert res.status_code == HTTPStatus.OK


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

    assert res.status_code == HTTPStatus.OK
    # We only get the patients the provider has permissions to view
    assert len(res.context["patients"]) == 2


def test_patient_add(provider: User, organization: Organization) -> None:
    data = {
        "first_name": "Jacob",
        "last_name": "Newpatient",
        "date_of_birth": date(1961, 6, 6),
        "province": "BC",
        "phn": "9111111117",  # BC requires more specific PHN
    }

    client = Client()
    client.force_login(provider)
    res = client.post(
        reverse(
            "providers:patient_add",
            kwargs={
                "organization_id": organization.id,
            },
        ),
        data=data,
    )

    assert res.status_code == HTTPStatus.FOUND
    created_patient = Patient.objects.get(last_name="Newpatient")
    assert created_patient
    assert res.url == reverse(  # type: ignore[attr-defined]
        "providers:patient",
        kwargs={"patient_id": created_patient.id, "organization_id": organization.id},
    )
    assert provider.has_perm("view_patient", created_patient)
    assert provider.has_perm("create_task", created_patient)


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

    assert res.status_code == HTTPStatus.NOT_FOUND


def test_patient_add_deny_access_missing_perms(provider: User, organization: Organization) -> None:
    data = {
        "first_name": "Jacob",
        "last_name": "Newpatient",
        "date_of_birth": date(1961, 6, 6),
        "province": "BC",
        "phn": "9111111117",  # BC requires more specific PHN
    }

    provider_group = provider.groups.first()
    remove_perm("create_patient", provider_group, organization)

    client = Client()
    client.force_login(provider)
    res = client.post(
        reverse(
            "providers:patient_add",
            kwargs={
                "organization_id": organization.id,
            },
        ),
        data=data,
    )

    assert res.status_code == HTTPStatus.NOT_FOUND


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

    assert res.status_code == HTTPStatus.OK


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

    assert res.status_code == HTTPStatus.NOT_FOUND


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

    assert res.status_code == HTTPStatus.FOUND
    assert res.url == reverse(  # type: ignore[attr-defined]
        "providers:patient",
        kwargs={"patient_id": patient.id, "organization_id": organization.id},
    )
    patient.refresh_from_db()
    assert patient.last_name == "Newname"


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

    assert res.status_code == HTTPStatus.NOT_FOUND


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

    assert res.status_code == HTTPStatus.FOUND
    assert res.url == reverse(  # type:ignore [attr-defined]
        "providers:patient",
        kwargs={"organization_id": organization.id, "patient_id": patient.id},
    )


def test_patient_add_task_deny_access(user: User, organization: Organization, patient: Patient) -> None:
    client = Client()
    client.force_login(user)
    res = client.post(
        reverse(
            "providers:patient_add_task",
            kwargs={"organization_id": organization.id, "patient_id": patient.id},
        )
    )

    assert res.status_code == HTTPStatus.NOT_FOUND


def test_patient_cancel_task(provider: User, patient, organization) -> None:
    client = Client()
    client.force_login(provider)
    task = TaskFactory.create(patient=patient)
    res = client.post(
        reverse(
            "providers:patient_cancel_task",
            kwargs={
                "organization_id": organization.id,
                "patient_id": patient.id,
                "task_id": task.id,
            },
        )
    )

    assert res.status_code == HTTPStatus.FOUND
    assert res.url == reverse(  # type: ignore[attr-defined]
        "providers:patient",
        kwargs={"organization_id": organization.id, "patient_id": patient.id},
    )
    task.refresh_from_db()
    assert task.status == TaskStatus.CANCELLED


def test_patient_cancel_task_deny_access(user: User, patient, organization) -> None:
    client = Client()
    client.force_login(user)
    task = TaskFactory.create(patient=patient)
    res = client.post(
        reverse(
            "providers:patient_cancel_task",
            kwargs={
                "organization_id": organization.id,
                "patient_id": patient.id,
                "task_id": task.id,
            },
        )
    )

    assert res.status_code == HTTPStatus.NOT_FOUND


def test_patient_archive(provider: User, organization: Organization, patient: Patient) -> None:
    client = Client()
    client.force_login(provider)
    Encounter.objects.create(organization=organization, patient=patient, status=EncounterStatus.IN_PROGRESS)

    res = client.post(
        reverse(
            "providers:patient_archive",
            kwargs={"organization_id": organization.id, "patient_id": patient.id},
        )
    )

    assert res.status_code == HTTPStatus.FOUND
    assert res.url == reverse("providers:patient_list", kwargs={"organization_id": organization.id})  # type:ignore [attr-defined]


def test_patient_archive_deny_access(user: User, organization: Organization, patient: Patient) -> None:
    client = Client()
    # This user doesn't have change_encounter perms, only view
    client.force_login(user)
    Encounter.objects.create(organization=organization, patient=patient, status=EncounterStatus.IN_PROGRESS)

    res = client.post(
        reverse(
            "providers:patient_archive",
            kwargs={"organization_id": organization.id, "patient_id": patient.id},
        )
    )

    assert res.status_code == HTTPStatus.NOT_FOUND


def test_patient_resend_invite(template_fixture, provider: User, organization: Organization, mailoutbox) -> None:
    client = Client()
    client.force_login(provider)
    unclaimed_patient = PatientFactory.create(organization=organization, email="test@example.com")

    res = client.post(
        reverse(
            "providers:patient_resend_invite",
            kwargs={"organization_id": organization.id, "patient_id": unclaimed_patient.id},
        )
    )

    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [unclaimed_patient.email]
    assert res.status_code == HTTPStatus.FOUND
    assert res.url == reverse(  # type: ignore[attr-defined]
        "providers:patient",
        kwargs={"organization_id": organization.id, "patient_id": unclaimed_patient.id},
    )


def test_patient_resend_invite_deny_access(user: User, organization: Organization, mailoutbox) -> None:
    client = Client()
    client.force_login(user)
    unclaimed_patient = PatientFactory.create(organization=organization, email="test@example.com")
    res = client.post(
        reverse(
            "providers:patient_resend_invite",
            kwargs={"organization_id": organization.id, "patient_id": unclaimed_patient.id},
        )
    )
    assert len(mailoutbox) == 0
    assert res.status_code == HTTPStatus.NOT_FOUND
