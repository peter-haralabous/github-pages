from http import HTTPStatus

import pytest
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from django.http import HttpResponseRedirect
from django.test import Client
from django.test import RequestFactory
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from sandwich.core.factories import ConsentFactory
from sandwich.core.models import Organization
from sandwich.core.models.consent import ConsentPolicy
from sandwich.users.factories import UserFactory
from sandwich.users.forms import UserAdminChangeForm
from sandwich.users.models import User
from sandwich.users.views import UserRedirectView
from sandwich.users.views import UserUpdateView
from sandwich.users.views import user_detail_view

pytestmark = pytest.mark.django_db


class TestUserUpdateView:
    """
    TODO:
        extracting view initialization code as class-scoped fixture
        would be great if only pytest-django supported non-function-scoped
        fixture db access -- this is a work-in-progress for now:
        https://github.com/pytest-dev/pytest-django/pull/258
    """

    def dummy_get_response(self, request: HttpRequest):
        return None

    def test_get_success_url(self, user: User, rf: RequestFactory):
        view = UserUpdateView()
        request = rf.get("/fake-url/")
        request.user = user

        view.request = request
        assert view.get_success_url() == f"/users/{user.pk}/"

    def test_get_object(self, user: User, rf: RequestFactory):
        view = UserUpdateView()
        request = rf.get("/fake-url/")
        request.user = user

        view.request = request

        assert view.get_object() == user

    def test_form_valid(self, user: User, rf: RequestFactory):
        view = UserUpdateView()
        request = rf.get("/fake-url/")

        # Add the session/message middleware to the request
        SessionMiddleware(self.dummy_get_response).process_request(request)
        MessageMiddleware(self.dummy_get_response).process_request(request)
        request.user = user

        view.request = request

        # Initialize the form
        form = UserAdminChangeForm()
        form.cleaned_data = {}
        form.instance = user
        view.form_valid(form)

        messages_sent = [m.message for m in messages.get_messages(request)]
        assert messages_sent == [_("Information successfully updated")]


class TestUserRedirectView:
    def test_get_redirect_url(self, user: User, rf: RequestFactory):
        view = UserRedirectView()
        request = rf.get("/fake-url")
        request.user = user

        view.request = request
        assert view.get_redirect_url() == f"/users/{user.pk}/"


class TestUserDetailView:
    def test_authenticated(self, user: User, rf: RequestFactory):
        request = rf.get("/fake-url/")
        request.user = UserFactory()  # type: ignore[assignment]
        response = user_detail_view(request, pk=user.pk)

        assert response.status_code == HTTPStatus.OK

    def test_not_authenticated(self, user: User, rf: RequestFactory):
        request = rf.get("/fake-url/")
        request.user = AnonymousUser()
        response = user_detail_view(request, pk=user.pk)
        login_url = reverse(settings.LOGIN_URL)

        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == f"{login_url}?next=/fake-url/"


class TestAccountDeleteView:
    def test_account_delete_authentication(self, db) -> None:
        # Try unauth'd
        client = Client()
        url = reverse("accounts:delete")
        response = client.get(url)
        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == 302  # Redirect to login
        assert reverse("account_login") in response.url

        # Try auth'd
        user = UserFactory.create()
        client.force_login(user)
        response = client.get(url)
        assert response.status_code == 200
        assert response.templates[0].name == "users/account_delete.html"

    def test_account_delete_post_valid_form(self, db, user: User, organization: Organization) -> None:
        ConsentFactory.create(user=user, policy=ConsentPolicy.THRIVE_TERMS_OF_USE, decision=True)
        ConsentFactory.create(user=user, policy=ConsentPolicy.THRIVE_PRIVACY_POLICY, decision=True)

        client = Client()
        client.force_login(user)
        url = reverse("accounts:delete")
        response = client.post(url, data={"confirmation": "DELETE"})

        assert response.status_code == 302
        assert isinstance(response, HttpResponseRedirect)
        assert reverse("account_login") in response.url

        # Note: User.delete_account() model tests covers associated entity deletion exhaustively
        assert User.objects.filter(pk=user.pk).exists() is False

        # Try to access a protected route
        response = client.get(reverse("patients:patient_add"))
        assert response.status_code == 302  # Middleware redirects user to login
        assert isinstance(response, HttpResponseRedirect)
        assert reverse("account_login") in response.url
