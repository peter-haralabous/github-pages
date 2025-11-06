import pytest
from django.test import Client
from django.urls import reverse

from sandwich.core.factories.invitation import InvitationFactory
from sandwich.core.factories.patient import PatientFactory
from sandwich.core.factories.task import TaskFactory
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.organization import Organization
from sandwich.core.models.role import RoleName
from sandwich.users.models import User


@pytest.mark.django_db
def test_accept_invite(user: User) -> None:
    patient = PatientFactory.create()
    invitation = InvitationFactory.create(patient=patient)
    client = Client()
    client.force_login(user)

    res = client.post(reverse("patients:accept_invite", kwargs={"token": invitation.token}), data={"accepted": True})

    assert res.status_code == 302
    assert res.url == reverse("patients:patient_details", kwargs={"patient_id": patient.id})  # type:ignore [attr-defined]
    patient.refresh_from_db()
    assert patient.user == user
    assert user.has_perm("change_patient", patient)


@pytest.mark.django_db
def test_accept_invite_with_organization(user: User, organization: Organization) -> None:
    patient = PatientFactory.create(organization=organization)
    invitation = InvitationFactory.create(patient=patient)
    client = Client()
    client.force_login(user)

    res = client.post(reverse("patients:accept_invite", kwargs={"token": invitation.token}), data={"accepted": True})

    assert res.status_code == 302
    assert res.url == reverse("patients:patient_details", kwargs={"patient_id": patient.id})  # type:ignore [attr-defined]
    organization_patient_group = organization.get_role(RoleName.PATIENT).group
    assert user.groups.get(name=organization_patient_group.name)


@pytest.mark.django_db
def test_accept_invite_with_provider_created_patient(provider: User, user: User, organization: Organization) -> None:
    # Invite entities created before user claim
    patient = PatientFactory.create(organization=organization)
    invite_encounter = Encounter.objects.create(
        organization=organization, patient=patient, status=EncounterStatus.IN_PROGRESS
    )
    invite_task = TaskFactory.create(patient=patient, encounter=invite_encounter)

    invitation = InvitationFactory.create(patient=patient)
    client = Client()
    client.force_login(user)

    res = client.post(reverse("patients:accept_invite", kwargs={"token": invitation.token}), data={"accepted": True})

    assert res.status_code == 302
    assert res.url == reverse("patients:patient_details", kwargs={"patient_id": patient.id})  # type:ignore [attr-defined]

    assert provider.has_perm("view_patient", patient)

    assert user.has_perm("view_task", invite_task)
    assert user.has_perm("view_encounter", invite_encounter)
