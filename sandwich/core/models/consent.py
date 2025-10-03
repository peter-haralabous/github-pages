from django.db import models

from sandwich.core.models.abstract import BaseModel
from sandwich.users.models import User


# TODO-NG: should these identifiers include a date in the name?
#          i.e. THRIVE_PRIVACY_POLICY_2024_01
class ConsentPolicy(models.TextChoices):
    THRIVE_TERMS_OF_USE = "THRIVE_TERMS_OF_USE"
    THRIVE_PRIVACY_POLICY = "THRIVE_PRIVACY_POLICY"
    # THRIVE_AI_POLICY = "THRIVE_AI_POLICY"
    # THRIVE_MARKETING_POLICY = "THRIVE_MARKETING_POLICY"


class ConsentManager(models.Manager["Consent"]):
    def for_user(self, user: User):
        """
        Fetch Consent records for the given user. Only the latest record for each policy is relevant.
        """
        return self.filter(user=user).order_by("policy", "-date").distinct("policy")


class Consent(BaseModel):
    """
    Consent tracks a User's consent to a specified policy.

    Do not update Consent records once they have been created; instead, create a new record with the updated decision.

    We're currently only modelling Users consenting to Thrive policies, but this should be extensible to support
    management of Organization-provided policies and perhaps Patient-level consent as well.

    See https://www.hl7.org/fhir/consent.html
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    policy = models.CharField(max_length=255, choices=ConsentPolicy)
    decision = models.BooleanField()  # in FHIR this is "deny"/"permit" as a string code
    date = models.DateTimeField(auto_now_add=True)

    objects = ConsentManager()
