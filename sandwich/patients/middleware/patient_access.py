import logging
from collections.abc import Callable

from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse

from sandwich.core.models.patient import Patient
from sandwich.core.util.http import cached_resolve

logger = logging.getLogger(__name__)


class PatientAccessMiddleware:
    """
    Detect when someone is about to go to a patient URL, but has no patient of their own currently.
    """

    _allowed_routes = [
        "patients:accept_invite",
        "patients:patient_onboarding_add",
    ]
    """These routes are allowed to be visited without the user having an associated patient yet."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.user and request.user.is_authenticated:
            # We want to check for any url that starts with "patient/" that isn't "patient/add"
            # to avoid a redirect loop.
            match = cached_resolve(request)

            if match.namespace == "patients" and match.view_name not in self._allowed_routes:
                has_patient = Patient.objects.filter(user=request.user).exists()
                if not has_patient:
                    logger.info("User has no patient, redirecting to add patient", extra={"user_id": request.user.id})
                    return HttpResponseRedirect(reverse("patients:patient_onboarding_add"))

        return self.get_response(request)
