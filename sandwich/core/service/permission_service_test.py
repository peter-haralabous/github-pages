import pytest
from django.http import Http404

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models.organization import Organization
from sandwich.core.models.patient import Patient
from sandwich.core.service.permissions_service import ObjectNameCollisionError
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.testing import UserRequestFactory
from sandwich.users.models import User


@pytest.mark.django_db
def test_authorize_objects(provider: User, organization: Organization, urf: UserRequestFactory) -> None:
    request = urf(provider).get("/")

    @authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization"])])
    def func(request, **kwargs):
        return kwargs.get("organization")

    assert func(request, organization_id=organization.id)
    assert isinstance(func(request, organization_id=organization.id), Organization)


@pytest.mark.django_db
def test_authorize_objects_multiple_objects(
    provider: User, organization: Organization, patient: Patient, urf: UserRequestFactory
) -> None:
    request = urf(provider).get("/")

    @authorize_objects(
        [
            ObjPerm(Organization, "organization_id", ["view_organization"]),
            ObjPerm(Patient, "patient_id", ["view_patient"]),
        ]
    )
    def func(request, **kwargs) -> tuple:
        return (kwargs.get("patient"), kwargs.get("organization"))

    patient, org = func(request, organization_id=organization.id, patient_id=patient.id)
    assert isinstance(org, Organization)
    assert isinstance(patient, Patient)


@pytest.mark.django_db
def test_authorize_objects_override_object_name(
    provider: User, organization: Organization, patient: Patient, urf: UserRequestFactory
) -> None:
    request = urf(provider).get("/")

    @authorize_objects(
        [
            ObjPerm(Organization, "organization_id", ["view_organization"], "renamed_org"),
            ObjPerm(Patient, "patient_id", ["view_patient"], "renamed_patient"),
        ]
    )
    def func(request, **kwargs) -> None:
        assert kwargs.get("patient") is None
        assert kwargs.get("organization") is None
        assert kwargs.get("renamed_org")
        assert kwargs.get("renamed_patient")

    func(request, organization_id=organization.id, patient_id=patient.id)


@pytest.mark.django_db
def test_authorize_objects_object_name_collision(
    provider: User, organization: Organization, patient: Patient, urf: UserRequestFactory
) -> None:
    patient_2 = PatientFactory.create(organization=organization)
    request = urf(provider).get("/")

    @authorize_objects(
        [ObjPerm(Patient, "src_patient_id", ["view_patient"]), ObjPerm(Patient, "dest_patient_id", ["view_patient"])]
    )
    def func(request, **kwargs) -> None:
        pass

    with pytest.raises(ObjectNameCollisionError):
        func(request, src_patient_id=patient.id, dest_patient_id=patient_2.id)


@pytest.mark.django_db
def test_authorize_objects_deny_access_no_permissions(
    user: User, organization: Organization, urf: UserRequestFactory
) -> None:
    # User does not have a connection to this org
    request = urf(user).get("/")

    @authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization"])])
    def func(request, **kwargs):
        return kwargs.get("organization")

    with pytest.raises(Http404):
        func(request, organization_id=organization.id)


@pytest.mark.django_db
def test_authorize_objects_deny_access_not_all_permissions(
    provider: User, organization: Organization, urf: UserRequestFactory
) -> None:
    request = urf(provider).get("/")

    @authorize_objects(
        [
            # Does not have `delete_organization` access
            ObjPerm(Organization, "organization_id", ["view_organization", "delete_organizaiton"])
        ]
    )
    def func(request, **kwargs):
        return kwargs.get("organization")

    with pytest.raises(Http404):
        func(request, organization_id=organization.id)


@pytest.mark.django_db
def test_authorize_objects_deny_access_multiple_objects(
    provider: User, organization: Organization, patient: Patient, urf: UserRequestFactory
) -> None:
    request = urf(provider).get("/")

    @authorize_objects(
        [
            ObjPerm(Organization, "organization_id", ["view_organization"]),
            # Does not have `delete_patient` access
            ObjPerm(Patient, "patient_id", ["view_patient", "delete_patient"]),
        ]
    )
    def func(request, **kwargs) -> tuple:
        return (kwargs.get("patient"), kwargs.get("organization"))

    with pytest.raises(Http404):
        func(request, organization_id=organization.id, patient_id=patient.id)
