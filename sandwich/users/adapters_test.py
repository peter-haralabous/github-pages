from types import SimpleNamespace

import pytest
from allauth.account.internal.flows.password_reset import request_password_reset
from allauth.account.internal.flows.signup import send_unknown_account_mail
from allauth.core.context import request_context
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from sandwich.users.factories import UserFactory


@pytest.fixture
def allauth_request(rf: RequestFactory):
    request = rf.get("/")  # the details of the request don't really matter
    request.user = AnonymousUser()

    with request_context(request):
        yield request


@pytest.mark.django_db
def test_unknown_account_email(
    template_fixture: None,
    allauth_request,
    mailoutbox,
    snapshot_html,
) -> None:
    send_unknown_account_mail(allauth_request, "nobody@example.com")

    assert len(mailoutbox) == 1
    email = mailoutbox[0]
    assert email.subject == "Unknown Account"
    assert email.body == snapshot_html


@pytest.mark.django_db
def test_password_reset_email(
    template_fixture: None,
    allauth_request,
    mailoutbox,
    snapshot_html,
) -> None:
    user = UserFactory.build(id=1)
    token_generator = SimpleNamespace(make_token=lambda _: "abracadabra")
    request_password_reset(allauth_request, user.email, [user], token_generator)

    assert len(mailoutbox) == 1
    email = mailoutbox[0]
    assert email.subject == "Password Reset Email"
    assert email.body == snapshot_html
