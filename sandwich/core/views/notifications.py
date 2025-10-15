import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import get_messages
from django.http import HttpResponse
from django.shortcuts import render

from sandwich.core.models.consent import ConsentPolicy
from sandwich.core.service.consent_service import latest_for_user_policy
from sandwich.core.service.consent_service import record_consent
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


@login_required
def account_notifications(request: AuthenticatedHttpRequest) -> HttpResponse:
    if last_consent := latest_for_user_policy(request.user, ConsentPolicy.THRIVE_MARKETING_POLICY):
        decision = last_consent.decision
    else:
        decision = False

    if request.method == "POST":
        decision = bool(request.POST.get("decision"))
        [consent] = record_consent(request.user, {ConsentPolicy.THRIVE_MARKETING_POLICY: decision})
        logger.info(
            "Marketing consent decision updated",
            extra={
                "user_id": request.user.id,
                "consent_id": consent.id,
                "decision": consent.decision,
            },
        )
        messages.add_message(request, messages.SUCCESS, "Your decision has been recorded.")

        # If this is an htmx request, leverage the OOB swap capabilities of this partial.
        if request.headers.get("HX-Request") == "true":
            return render(request, "partials/messages.html", {"messages": get_messages(request)})

    return render(request, "users/account_notifications.html", {"decision": decision})
