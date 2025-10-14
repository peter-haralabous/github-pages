from unittest.mock import patch

import pytest
from django.test import Client
from django.urls import reverse

from sandwich.core.factories import ConsentFactory
from sandwich.core.middleware.consent import _has_consented_to_policies
from sandwich.core.models.consent import Consent
from sandwich.core.models.consent import ConsentPolicy
from sandwich.users.models import User


@pytest.fixture
def privacy_consent(user_wo_consent: User) -> Consent:
    return ConsentFactory.create(user=user_wo_consent, policy=ConsentPolicy.THRIVE_PRIVACY_POLICY, decision=True)


@pytest.fixture
def tou_consent(user_wo_consent: User) -> Consent:
    return ConsentFactory.create(user=user_wo_consent, policy=ConsentPolicy.THRIVE_TERMS_OF_USE, decision=True)


@pytest.fixture
def tou_refusal(user_wo_consent: User) -> Consent:
    return ConsentFactory.create(user=user_wo_consent, policy=ConsentPolicy.THRIVE_TERMS_OF_USE, decision=False)


def test__has_consented_to_policies(privacy_consent: Consent, tou_consent: Consent, user_wo_consent: User) -> None:
    assert _has_consented_to_policies(user_wo_consent, {ConsentPolicy.THRIVE_PRIVACY_POLICY}) is True
    assert _has_consented_to_policies(user_wo_consent, {ConsentPolicy.THRIVE_TERMS_OF_USE}) is True
    assert (
        _has_consented_to_policies(
            user_wo_consent, {ConsentPolicy.THRIVE_PRIVACY_POLICY, ConsentPolicy.THRIVE_TERMS_OF_USE}
        )
        is True
    )


def test__has_consented_to_policies_rejected(
    privacy_consent: Consent, tou_refusal: Consent, user_wo_consent: User
) -> None:
    assert _has_consented_to_policies(user_wo_consent, {ConsentPolicy.THRIVE_PRIVACY_POLICY}) is True
    assert _has_consented_to_policies(user_wo_consent, {ConsentPolicy.THRIVE_TERMS_OF_USE}) is False
    assert (
        _has_consented_to_policies(
            user_wo_consent, {ConsentPolicy.THRIVE_PRIVACY_POLICY, ConsentPolicy.THRIVE_TERMS_OF_USE}
        )
        is False
    )


def test_middleware(client: Client, user_wo_consent: User) -> None:
    client.force_login(user_wo_consent)

    with patch("sandwich.core.middleware.consent._handle_missing_consent") as mock_handle_missing_consent:
        client.get(reverse("core:home"))
        mock_handle_missing_consent.assert_called_once()


def test_middleware_consented(
    client: Client,
    user_wo_consent: User,
    privacy_consent: Consent,
    tou_consent: Consent,
) -> None:
    client.force_login(user_wo_consent)

    with patch("sandwich.core.middleware.consent._handle_missing_consent") as mock_handle_missing_consent:
        client.get(reverse("core:home"))
        mock_handle_missing_consent.assert_not_called()


def test_middleware_exempt(client: Client, user_wo_consent: User) -> None:
    client.force_login(user_wo_consent)

    with patch("sandwich.core.middleware.consent._handle_missing_consent") as mock_handle_missing_consent:
        client.get(reverse("core:healthcheck"))
        mock_handle_missing_consent.assert_not_called()
