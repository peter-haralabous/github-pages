from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

from sandwich.core.factories.consent import ConsentFactory
from sandwich.core.middleware.consent import ConsentMiddleware
from sandwich.core.models.consent import ConsentPolicy

if TYPE_CHECKING:
    from sandwich.users.models import User


pytestmark = pytest.mark.django_db


def test_legal_view_shows_policy_blocks_for_consents(db, client, user: User) -> None:
    """
    When a user has consents, the corresponding policy blocks appear in the response.
    """
    # Ensure the user has the relevant consents; factory will create appropriate records
    ConsentFactory.create(user=user, policy=ConsentPolicy.THRIVE_PRIVACY_POLICY, decision=True)
    ConsentFactory.create(user=user, policy=ConsentPolicy.THRIVE_TERMS_OF_USE, decision=True)

    # Use the pytest-django `client` fixture to exercise middleware and ensure
    # the view is accessible when the user has consented to the required policies.
    # Note: we still call client.force_login(user) to authenticate the test user.
    client.force_login(user)
    response = client.get(reverse("core:legal"))
    assert response.status_code == 200
    content = response.content.decode("utf-8")

    # The template shows human-readable headings for each policy
    assert "Privacy Policy" in content
    assert "Terms of Use" in content


def test_legal_view_renders_when_required_policies_reduced(db, client, user: User, monkeypatch) -> None:
    """
    If we temporarily reduce the set of required policies, the middleware
    will permit access and the template should render without showing blocks
    for policies that are not required.
    """
    # Give the user only the privacy consent and decline terms
    ConsentFactory.create(user=user, policy=ConsentPolicy.THRIVE_PRIVACY_POLICY, decision=True)
    ConsentFactory.create(user=user, policy=ConsentPolicy.THRIVE_TERMS_OF_USE, decision=False)

    # Reduce the middleware's required_policies so Terms of Use is NOT required
    monkeypatch.setattr(ConsentMiddleware, "required_policies", {ConsentPolicy.THRIVE_PRIVACY_POLICY})

    client.force_login(user)
    response = client.get(reverse("core:legal"))
    assert response.status_code == 200
    content = response.content.decode("utf-8")

    # The template should still show Privacy but not Terms
    assert "Privacy Policy" in content
    assert "Terms of Use" not in content


def test_legal_view_renders_when_no_policies_required(db, client, user_wo_consent: User, monkeypatch) -> None:
    """
    If no policies are required, the view should render even if the user
    has explicitly declined all policies; no policy blocks should be shown.
    """
    # Make the middleware require nothing so we can access the view.
    monkeypatch.setattr(ConsentMiddleware, "required_policies", set())

    client.force_login(user_wo_consent)
    response = client.get(reverse("core:legal"))
    assert response.status_code == 200
    content = response.content.decode("utf-8")

    # Neither policy block should be shown
    assert "Privacy Policy" not in content
    assert "Terms of Use" not in content
    # Ensure the existing template fallback is present
    assert "No policies found!" in content
