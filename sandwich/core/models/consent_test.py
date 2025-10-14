import pytest
from django.utils import timezone

from sandwich.core.models import Consent
from sandwich.core.models.consent import ConsentPolicy
from sandwich.users.models import User


def test_for_user(user_wo_consent: User):
    assert Consent.objects.for_user(user_wo_consent).count() == 0

    # first, consent to privacy policy
    Consent.objects.create(
        user=user_wo_consent, policy=ConsentPolicy.THRIVE_PRIVACY_POLICY, decision=True, date=timezone.now()
    )
    assert Consent.objects.for_user(user_wo_consent).count() == 1
    consent = Consent.objects.for_user(user_wo_consent).get(policy=ConsentPolicy.THRIVE_PRIVACY_POLICY)
    assert consent.decision is True

    # then consent to terms of use
    Consent.objects.create(
        user=user_wo_consent, policy=ConsentPolicy.THRIVE_TERMS_OF_USE, decision=True, date=timezone.now()
    )
    assert Consent.objects.for_user(user_wo_consent).count() == 2

    # then revoke consent to privacy policy
    Consent.objects.create(
        user=user_wo_consent, policy=ConsentPolicy.THRIVE_PRIVACY_POLICY, decision=False, date=timezone.now()
    )
    assert Consent.objects.for_user(user_wo_consent).count() == 2
    consent = Consent.objects.for_user(user_wo_consent).get(policy=ConsentPolicy.THRIVE_PRIVACY_POLICY)
    assert consent.decision is False


@pytest.mark.xfail(reason="Filtering by decision gives the wrong result.")
def test_for_user_filter_by_decision(user_wo_consent: User):
    Consent.objects.create(
        user=user_wo_consent, policy=ConsentPolicy.THRIVE_PRIVACY_POLICY, decision=True, date=timezone.now()
    )
    Consent.objects.create(
        user=user_wo_consent, policy=ConsentPolicy.THRIVE_PRIVACY_POLICY, decision=False, date=timezone.now()
    )

    consents = Consent.objects.for_user(user_wo_consent).filter(decision=True)
    assert consents.count() == 0
