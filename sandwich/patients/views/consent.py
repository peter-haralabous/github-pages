import logging

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.safestring import mark_safe

from sandwich.core.models.consent import ConsentPolicy
from sandwich.core.service.consent_service import record_consent
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)

_blank_link = '<a class="link" target="_blank" href="%s">%s</a>'
tos_link = _blank_link % ("https://www.thrive.health/terms", "Terms of Use")
privacy_link = _blank_link % ("https://www.thrive.health/privacynotice", "Privacy Policy")


class PatientConsentForm(forms.Form):
    required = forms.BooleanField(
        required=True,
        label=mark_safe(f"I agree to the {tos_link} and {privacy_link}"),  # noqa: S308
        help_text="I consent to the use of my health data to power the features within this application.",
    )
    marketing = forms.BooleanField(
        required=False,
        label="Stay up to date (Optional))",
        help_text="Receive occasional emails such as updates on features, tips, and promotional content",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("continue", "Continue", fieldclasses="btn btn-primary w-full"))


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
        return HttpResponseRedirect(request.GET.get("next", "patients:home"))

    context = {"form": form}
    return render(request, "patient/patient_consent.html", context)
