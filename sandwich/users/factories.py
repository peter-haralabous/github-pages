from collections.abc import Sequence
from typing import Any

from allauth.account.models import EmailAddress
from factory import Faker
from factory import post_generation
from factory.django import DjangoModelFactory

from sandwich.core.service.consent_service import record_consent
from sandwich.users.models import User


class EmailAddressFactory(DjangoModelFactory[EmailAddress]):
    class Meta:
        model = EmailAddress
        django_get_or_create = ["user", "email"]


class UserFactory(DjangoModelFactory[User]):
    email = Faker("email")
    name = Faker("name")

    def __init__(self):
        self.password = None
        self.consents = None

    @post_generation
    def groups(self: User, create: bool, extracted: Sequence[Any], **kwargs):  # noqa: FBT001
        if create and extracted:
            self.groups.add(*extracted)

    @post_generation
    def password(self: User, create: bool, extracted: Sequence[Any], **kwargs):  # noqa: FBT001
        password = (
            extracted
            if extracted
            else Faker(
                "password",
                length=42,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ).evaluate(None, None, extra={"locale": None})
        )
        self.set_password(password)  # type: ignore[arg-type]
        self.raw_password = password

    @post_generation
    def consents(self: User, create: bool, extracted: Sequence[Any], **kwargs):  # noqa: FBT001
        if create and extracted:
            record_consent(user=self, decisions=dict.fromkeys(extracted, True))

    @post_generation
    def email_address(self: User, create: bool, extracted: Sequence[Any], **kwargs):  # noqa: FBT001
        """Compatibility with allauth.account.EmailAddress; Create primary verified email address for the user."""
        if create:
            EmailAddressFactory.create(user=self, email=self.email, primary=True, verified=True)

    @classmethod
    def _after_postgeneration(cls, instance, create, results=None):
        if create:
            # Persist any in-place modifications made by post-generation hooks.
            instance.save()

    class Meta:
        model = User
        django_get_or_create = ["email"]
