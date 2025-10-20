from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.core import mail

from sandwich.core.factories.template import TemplateFactory
from sandwich.core.models import Template
from sandwich.users.adapters import AccountAdapter
from sandwich.users.models import User


class MockRequest:
    @staticmethod
    def get_host():
        return "mocked_get_host"


@pytest.fixture
def mock_request():
    return MockRequest()


@pytest.fixture
def mock_context(mock_request: MockRequest) -> SimpleNamespace:
    return SimpleNamespace(request=mock_request)


@pytest.fixture
def password_reset_subject_template() -> Template:
    return TemplateFactory(slug="account/email/password_reset_key_subject.txt", content="SUBJECT")  # type: ignore[return-value]


@pytest.fixture
def password_reset_message_template() -> Template:
    return TemplateFactory(slug="account/email/password_reset_key_message.txt", content="MESSAGE")  # type: ignore[return-value]


def test_account_email(
    user: User,
    mock_context: SimpleNamespace,
    password_reset_subject_template: Template,
    password_reset_message_template: Template,
) -> None:
    with patch("allauth.account.adapter.globals") as mock_globals:
        mock_globals.return_value = {"context": mock_context}
        AccountAdapter().send_password_reset_mail(user, user.email, {})
    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert email.subject == "SUBJECT"
    assert email.body == "<p>MESSAGE</p>\n"
