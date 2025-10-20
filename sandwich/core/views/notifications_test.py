import pytest
from django.test import Client
from django.urls import reverse

from sandwich.core.factories.consent import ConsentFactory
from sandwich.core.models import Consent
from sandwich.core.models.consent import ConsentPolicy
from sandwich.users.models import User


@pytest.mark.django_db
def test_account_notifications_get_no_prior_consent(client: Client, user: User):
    client.force_login(user)
    url = reverse("core:account_notifications")
    response = client.get(url)
    assert response.status_code == 200
    assert response.context["decision"] is False


@pytest.mark.django_db
def test_account_notifications_get_with_prior_consent(client: Client, user: User):
    ConsentFactory.create(user=user, policy=ConsentPolicy.THRIVE_MARKETING_POLICY, decision=True)
    client.force_login(user)
    url = reverse("core:account_notifications")
    response = client.get(url)
    assert response.status_code == 200
    assert response.context["decision"] is True


@pytest.mark.django_db
def test_account_notifications_post_decision_true(client: Client, user: User):
    client.force_login(user)
    url = reverse("core:account_notifications")
    response = client.post(url, data={"decision": "on"})

    assert response.status_code == 200
    assert response.context["decision"] is True
    assert "users/account_notifications.html" in (t.name for t in response.templates)

    consent = Consent.objects.get(user=user, policy=ConsentPolicy.THRIVE_MARKETING_POLICY)
    assert consent.decision is True


@pytest.mark.django_db
def test_account_notifications_post_decision_false(client: Client, user: User):
    ConsentFactory.create(user=user, policy=ConsentPolicy.THRIVE_MARKETING_POLICY, decision=True)
    client.force_login(user)
    url = reverse("core:account_notifications")
    response = client.post(url, data={})  # No "decision" in POST data

    assert response.status_code == 200
    assert response.context["decision"] is False
    assert "users/account_notifications.html" in (t.name for t in response.templates)

    latest_consent = Consent.objects.filter(user=user, policy=ConsentPolicy.THRIVE_MARKETING_POLICY).latest("date")
    assert latest_consent.decision is False


@pytest.mark.django_db
def test_account_notifications_post_htmx(client: Client, user: User):
    client.force_login(user)
    url = reverse("core:account_notifications")
    response = client.post(url, data={"decision": "on"}, headers={"HX-Request": "true"})

    assert response.status_code == 200
    assert "partials/message_item.html" in {t.name for t in response.templates}

    consent = Consent.objects.get(user=user, policy=ConsentPolicy.THRIVE_MARKETING_POLICY)
    assert consent.decision is True
