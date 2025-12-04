import pytest
from django.http import HttpResponseRedirect
from django.test import Client
from django.urls import reverse

from sandwich.core.factories.consent import ConsentFactory
from sandwich.core.models import Organization
from sandwich.core.models.consent import ConsentPolicy
from sandwich.users.models import User

pytestmark = pytest.mark.django_db


def test_account_delete_post_valid_form(db, user: User, organization: Organization) -> None:
    ConsentFactory.create(user=user, policy=ConsentPolicy.THRIVE_TERMS_OF_USE, decision=True)
    ConsentFactory.create(user=user, policy=ConsentPolicy.THRIVE_PRIVACY_POLICY, decision=True)

    client = Client()
    client.force_login(user)
    url = reverse("core:account_delete")
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
