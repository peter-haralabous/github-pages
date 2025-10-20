import factory
from factory.django import DjangoModelFactory

from sandwich.core.models import Consent
from sandwich.core.models.consent import ConsentPolicy


class ConsentFactory(DjangoModelFactory[Consent]):
    user = factory.SubFactory("sandwich.users.factories.UserFactory")
    policy = ConsentPolicy.THRIVE_PRIVACY_POLICY
    decision = True

    class Meta:
        model = Consent
        skip_postgeneration_save = True
