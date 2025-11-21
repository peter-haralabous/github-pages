import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from sandwich.core.models.consent import ConsentPolicy
from sandwich.core.service.consent_service import record_consent
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.patients.forms.consent import PatientConsentForm

logger = logging.getLogger(__name__)


@login_required
def patient_consent(request: AuthenticatedHttpRequest) -> HttpResponse:
    logger.info("User accessing patient consent", extra={"user_id": request.user.id})

    form = PatientConsentForm(request.POST or None)
    if form.is_valid():
        record_consent(
            request.user,
            {
                ConsentPolicy.THRIVE_PRIVACY_POLICY: form.cleaned_data["required"],
                ConsentPolicy.THRIVE_TERMS_OF_USE: form.cleaned_data["required"],
                ConsentPolicy.THRIVE_MARKETING_POLICY: form.cleaned_data["marketing"],
            },
        )
        return HttpResponseRedirect(redirect_to=request.GET.get("next", reverse("patients:home")))

    context = {"form": form}
    return render(request, "patient/patient_consent.html", context)
