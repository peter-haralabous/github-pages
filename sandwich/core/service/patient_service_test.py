import pytest

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models.organization import Organization
from sandwich.users.factories import UserFactory
from sandwich.users.models import User


@pytest.mark.django_db
def test_assign_default_patient_permissions_provider_created(
    user: User, provider: User, organization: Organization
) -> None:
    new_patient = PatientFactory.create(organization=organization)

    assert provider.has_perm("view_patient", new_patient)
    assert provider.has_perm("change_patient", new_patient)
    assert provider.has_perm("assign_task", new_patient)

    # random user doesn't have perms
    assert user.has_perm("view_patient", new_patient) is False
    assert user.has_perm("change_patient", new_patient) is False
    assert user.has_perm("assign_task", new_patient) is False


@pytest.mark.django_db
def test_assign_default_patient_permissions_user_created(user: User) -> None:
    other_user = UserFactory.create()

    new_patient = PatientFactory.create(user=user)

    assert user.has_perm("view_patient", new_patient)
    assert user.has_perm("change_patient", new_patient)
    assert user.has_perm("delete_patient", new_patient)

    # random user doesn't have perms
    assert other_user.has_perm("view_patient", new_patient) is False
    assert other_user.has_perm("change_patient", new_patient) is False
    assert other_user.has_perm("assign_task", new_patient) is False
