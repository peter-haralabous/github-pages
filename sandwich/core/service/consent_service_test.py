# python
from datetime import timedelta

import pytest
from django.utils import timezone

from sandwich.core.models.consent import Consent
from sandwich.core.models.consent import ConsentPolicy
from sandwich.core.service.consent_service import latest_for_user_policy
from sandwich.core.service.consent_service import record_consent
from sandwich.users.models import User


@pytest.mark.django_db
def test_record_consent_creates_entries(user_wo_consent: User):
    decisions = {
        ConsentPolicy.THRIVE_PRIVACY_POLICY: True,
        ConsentPolicy.THRIVE_TERMS_OF_USE: False,
    }

    created = record_consent(user_wo_consent, decisions)

    assert len(created) == len(decisions)
    assert Consent.objects.filter(user=user_wo_consent).count() == len(decisions)
    for policy, expected in decisions.items():
        c = Consent.objects.get(user=user_wo_consent, policy=policy)
        assert c.decision is expected


@pytest.mark.django_db
def test_record_consent_multiple_calls_create_multiple_records(user_wo_consent: User):
    policy = ConsentPolicy.THRIVE_PRIVACY_POLICY

    record_consent(user_wo_consent, {policy: True})
    record_consent(user_wo_consent, {policy: False})

    qs = Consent.objects.filter(user=user_wo_consent, policy=policy)
    assert qs.count() == 2

    latest = latest_for_user_policy(user_wo_consent, policy)
    assert latest is not None
    assert latest.decision is False


@pytest.mark.django_db
def test_latest_for_user_wo_consent_policy_returns_none_when_missing(user_wo_consent: User):
    assert latest_for_user_policy(user_wo_consent, ConsentPolicy.THRIVE_PRIVACY_POLICY) is None


@pytest.mark.django_db
def test_latest_for_user_wo_consent_policy_returns_latest_by_date(user_wo_consent: User):
    policy = ConsentPolicy.THRIVE_PRIVACY_POLICY

    older = timezone.now() - timedelta(days=2)
    newer = timezone.now() - timedelta(days=1)

    Consent.objects.create(user=user_wo_consent, policy=policy, decision=True, date=older)
    Consent.objects.create(user=user_wo_consent, policy=policy, decision=False, date=newer)

    latest = latest_for_user_policy(user_wo_consent, policy)
    assert latest is not None
    assert latest.decision is False
    assert latest.date == newer
