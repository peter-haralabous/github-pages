import os

import pytest

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
