import os
from collections.abc import Iterable
from urllib.parse import urlparse

import factory
import pytest
from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY
from django.contrib.auth import HASH_SESSION_KEY
from django.contrib.auth import SESSION_KEY
from django.contrib.sessions.backends.db import SessionStore
from django.core.management import call_command
from syrupy.extensions.single_file import SingleFileSnapshotExtension
from syrupy.extensions.single_file import WriteMode

from sandwich.core.factories.providers.condition import ConditionProvider
from sandwich.core.util.testing import UserRequestFactory
from sandwich.fixtures.default import condition
from sandwich.fixtures.default import document
from sandwich.fixtures.default import encounter
from sandwich.fixtures.default import organization
from sandwich.fixtures.default import owner
from sandwich.fixtures.default import patient
from sandwich.fixtures.default import provider
from sandwich.fixtures.default import task
from sandwich.fixtures.default import user
from sandwich.fixtures.knowledge_graph import patient_entity
from sandwich.fixtures.knowledge_graph import patient_knowledge_graph
from sandwich.fixtures.other import other_condition
from sandwich.fixtures.other import other_document
from sandwich.fixtures.other import other_encounter
from sandwich.fixtures.other import other_organization
from sandwich.fixtures.other import other_owner
from sandwich.fixtures.other import other_patient
from sandwich.fixtures.other import other_provider
from sandwich.fixtures.other import other_task
from sandwich.fixtures.other import other_user
from sandwich.fixtures.webpack import conditional_webpack
from sandwich.users.factories import UserFactory
from sandwich.users.models import User

# For playwright tests, it uses async internally.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

__all__ = [
    "condition",
    "conditional_webpack",
    "document",
    "encounter",
    "organization",
    "other_condition",
    "other_document",
    "other_encounter",
    "other_organization",
    "other_organization",
    "other_owner",
    "other_patient",
    "other_provider",
    "other_task",
    "other_user",
    "owner",
    "patient",
    "patient_entity",
    "patient_knowledge_graph",
    "provider",
    "task",
    "user",
]


# Install custom providers
# https://faker.readthedocs.io/en/master/#how-to-create-a-provider
# https://factoryboy.readthedocs.io/en/stable/reference.html#faker
factory.Faker.add_provider(ConditionProvider)


@pytest.fixture(autouse=True)
def _media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def urf() -> UserRequestFactory:
    return UserRequestFactory()


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


def django_session_fixtures(fixtures: Iterable[str]):
    """Build a session fixture that loads some Django fixtures once per test session."""

    @pytest.fixture(scope="session")
    def load_data(django_db_setup, django_db_blocker):
        with django_db_blocker.unblock():
            call_command("loaddata", *fixtures)

    return load_data


template_fixture = django_session_fixtures(["template"])


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
        # by default VCR doesn't consider body when matching requests
        # when replaying LLM responses, the prompt matters _a lot_
        "match_on": ["method", "scheme", "host", "port", "path", "query", "body"],
    }


class SingleFileHtmlSnapshotExtension(SingleFileSnapshotExtension):
    _file_extension = "html"
    _write_mode = WriteMode.TEXT


@pytest.fixture
def snapshot_html(snapshot):
    """
    Syrupy fixture that write snapshots as individual HTML files.

    This makes it a lot easier to open the snapshot in a browser and ensure that it looks ok.
    """
    return snapshot.with_defaults(extension_class=SingleFileHtmlSnapshotExtension)
