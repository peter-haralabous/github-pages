from django.utils import timezone

from sandwich.core.models import Consent
from sandwich.core.models.consent import ConsentPolicy
from sandwich.users.models import User


def test_for_user(user: User):
    assert Consent.objects.for_user(user).count() == 0

    # first, consent to privacy policy
    Consent.objects.create(user=user, policy=ConsentPolicy.THRIVE_PRIVACY_POLICY, decision=True, date=timezone.now())
    assert Consent.objects.for_user(user).count() == 1
    consent = Consent.objects.for_user(user).get(policy=ConsentPolicy.THRIVE_PRIVACY_POLICY)
    assert consent.decision is True

    # then consent to terms of use
    Consent.objects.create(user=user, policy=ConsentPolicy.THRIVE_TERMS_OF_USE, decision=True, date=timezone.now())
    assert Consent.objects.for_user(user).count() == 2

    # then revoke consent to privacy policy
    Consent.objects.create(user=user, policy=ConsentPolicy.THRIVE_PRIVACY_POLICY, decision=False, date=timezone.now())
    assert Consent.objects.for_user(user).count() == 2
    consent = Consent.objects.for_user(user).get(policy=ConsentPolicy.THRIVE_PRIVACY_POLICY)
    assert consent.decision is False
