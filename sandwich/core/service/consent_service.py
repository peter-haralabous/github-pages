import logging

from sandwich.core.models.consent import Consent
from sandwich.core.models.consent import ConsentPolicy
from sandwich.users.models import User

logger = logging.getLogger(__name__)


def record_consent(user: User, decisions: dict[ConsentPolicy, bool]) -> list[Consent]:
    """Records the consent decisions for a user."""
    created = []
    for policy, decision in decisions.items():
        created.append(
            Consent.objects.create(
                user=user,
                policy=policy,
                decision=decision,
            )
        )
    return created


def latest_for_user_policy(user: User, policy: ConsentPolicy) -> Consent | None:
    """Retrieves the latest consent record for the given user and policy."""
    return Consent.objects.filter(user=user, policy=policy).order_by("-date").first()
