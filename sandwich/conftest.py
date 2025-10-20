import os
from collections.abc import Iterable

import pytest
from django.core.management import call_command

from sandwich.core.factories.organization import OrganizationFactory
from sandwich.core.factories.patient import PatientFactory
from sandwich.core.middleware import ConsentMiddleware
from sandwich.core.models import Organization
from sandwich.core.models import Patient
from sandwich.core.models.role import RoleName
from sandwich.core.util.testing import UserRequestFactory
from sandwich.users.factories import UserFactory
from sandwich.users.models import User

# For playwright tests, it uses async internally.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


@pytest.fixture(autouse=True)
def _media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def urf() -> UserRequestFactory:
    return UserRequestFactory()


@pytest.fixture
def user(db) -> User:
    return UserFactory.create(consents=ConsentMiddleware.required_policies)


@pytest.fixture
def user_wo_consent(db) -> User:
    return UserFactory.create(consents=None)


@pytest.fixture
def patient(organization: Organization, user: User) -> Patient:
    """
    Creates a user-owned patient
    """
    patient = PatientFactory.create(
        first_name="John", last_name="Doe", email="jdoe@example.com", organization=organization, user=user
    )
    patient.assign_user_owner_perms(user)
    return patient


@pytest.fixture
def organization(db) -> Organization:
    return OrganizationFactory.create(name="Test Organization")


@pytest.fixture
def provider(db, organization: Organization) -> User:
    return UserFactory.create(
        email="provider@organization.org",
        consents=ConsentMiddleware.required_policies,
        groups={role.group for role in organization.role_set.filter(name=RoleName.STAFF)},
    )


@pytest.fixture
def other_organization(db) -> Organization:
    return OrganizationFactory.create(name="Other")


def django_session_fixtures(fixtures: Iterable[str]):
    """Build a session fixture that loads some Django fixtures once per test session."""

    @pytest.fixture(scope="session")
    def load_data(django_db_setup, django_db_blocker):
        with django_db_blocker.unblock():
            call_command("loaddata", *fixtures)

    return load_data


@pytest.fixture(scope="module")
def vcr_config():
    def before_record_request(request):
        # skip requests to get temporary credentials from STS
        # these vary depending on how your AWS profiles are set up
        if request.host in ("sts.amazonaws.com", "sts.ca-central-1.amazonaws.com"):
            return None
        return request

    return {
        # strip sensitive headers by default
        "filter_headers": [("Authorization", None), ("X-Amz-Security-Token", None)],
        "before_record_request": before_record_request,
    }
