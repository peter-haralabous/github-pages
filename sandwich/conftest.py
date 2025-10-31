import os
from collections.abc import Iterable
from urllib.parse import urlparse

import pytest
from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY
from django.contrib.auth import HASH_SESSION_KEY
from django.contrib.auth import SESSION_KEY
from django.contrib.sessions.backends.db import SessionStore
from django.core.management import call_command

from sandwich.core.factories.organization import OrganizationFactory
from sandwich.core.middleware import ConsentMiddleware
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.organization import Organization
from sandwich.core.models.patient import Patient
from sandwich.core.models.role import RoleName
from sandwich.core.util.testing import UserRequestFactory
from sandwich.fixtures.patient import patient
from sandwich.fixtures.patient import patient_entity
from sandwich.fixtures.patient import patient_knowledge_graph
from sandwich.fixtures.webpack import conditional_webpack
from sandwich.users.factories import UserFactory
from sandwich.users.models import User

# For playwright tests, it uses async internally.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

__all__ = ["conditional_webpack", "patient", "patient_entity", "patient_knowledge_graph"]


@pytest.fixture(autouse=True)
def _media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def urf() -> UserRequestFactory:
    return UserRequestFactory()


@pytest.fixture
def encounter(organization: Organization, patient: Patient):
    return Encounter.objects.create(patient=patient, organization=organization, status=EncounterStatus.IN_PROGRESS)


@pytest.fixture
def user(db) -> User:
    return UserFactory.create(consents=ConsentMiddleware.required_policies)


@pytest.fixture
def auth_cookies(user, transactional_db, live_server, page):
    """Create a Django session for `user` and add its auth cookies to Playwright page."""
    session = SessionStore()
    session[SESSION_KEY] = str(user.pk)
    session[BACKEND_SESSION_KEY] = "django.contrib.auth.backends.ModelBackend"
    session[HASH_SESSION_KEY] = user.get_session_auth_hash()
    session.save()

    parsed = urlparse(live_server.url)
    domain = parsed.hostname or "localhost"

    cookie = {
        "name": settings.SESSION_COOKIE_NAME,
        "value": session.session_key,
        "domain": domain,
        "path": "/",
        "httpOnly": True,
    }

    page.context.add_cookies([cookie])
    return [cookie]


@pytest.fixture
def user_wo_consent(db) -> User:
    return UserFactory.create(consents=None)


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


template_fixture = django_session_fixtures(["template"])
