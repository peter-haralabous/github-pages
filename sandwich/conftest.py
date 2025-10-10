import os
from collections.abc import Iterable

import pytest
from django.core.management import call_command

from sandwich.core.factories import OrganizationFactory
from sandwich.core.models import Organization
from sandwich.users.factories import UserFactory
from sandwich.users.models import User

# For playwright tests, it uses async internally.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


@pytest.fixture(autouse=True)
def _media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory.create()


@pytest.fixture
def organization(db) -> Organization:
    return OrganizationFactory.create(name="Organization")


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
    return {
        # strip sensitive headers by default
        "filter_headers": [("Authorization", None), ("X-Amz-Security-Token", None)],
    }
