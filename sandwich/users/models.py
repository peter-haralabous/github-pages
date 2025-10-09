import logging
from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import transaction
from django.db.models import CharField
from django.db.models import EmailField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .managers import UserManager

logger = logging.getLogger(__name__)


class User(AbstractUser):
    """
    Default custom user model for sandwich.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    def initials(self) -> str:
        """
        1 or 2-letter abbreviation for the user, to be used in places like avatars.
        """
        return self.email[0].upper()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})

    def delete_account(self):
        """
        Deletes all objects associated with this user, then deletes the user itself.

        NOTE: This does not account for Many-to-Many relationships. None exist yet.

        Will delete related entries in:
        - admin.logentry
        - account.emailaddress
        - mfa.authenicator
        - socialaccount.socialaccount
        - core.consent
        - core.patient
        """
        with transaction.atomic():
            # For each User field, check if it's a relation.
            for rel in self._meta.get_fields():
                if (rel.one_to_many or rel.one_to_one) and rel.auto_created and not rel.concrete:
                    if rel_accessor_name := rel.get_accessor_name():  # type: ignore[union-attr]
                        related_manager = getattr(self, rel_accessor_name, None)
                        logger.info("Deleting related objects for relation: %s", rel)
                        if related_manager:
                            if rel.one_to_one:
                                obj = related_manager
                                if obj:
                                    obj.delete()
                            else:
                                related_manager.all().delete()
            self.delete()
