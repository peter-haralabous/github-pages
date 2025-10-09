import logging

from sandwich.core.models.consent import Consent
from sandwich.core.models.consent import ConsentPolicy
from sandwich.users.models import User

logger = logging.getLogger(__name__)


def record_consent(user: User, decisions: dict[ConsentPolicy, bool]) -> None:
    for policy, decision in decisions.items():
        Consent.objects.create(
            user=user,
            policy=policy,
            decision=decision,
        )
