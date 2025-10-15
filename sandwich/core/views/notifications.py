import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import get_messages
from django.http import HttpResponse
from django.shortcuts import render

from sandwich.core.models import Consent
from sandwich.core.models.consent import ConsentPolicy
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


@login_required
def account_notifications(request: AuthenticatedHttpRequest) -> HttpResponse:
    if last_consent := Consent.objects.latest_for_user_policy(request.user, ConsentPolicy.THRIVE_MARKETING_POLICY):
        decision = last_consent.decision
    else:
        decision = False

    if request.method == "POST":
        decision = bool(request.POST.get("decision"))
        consent = Consent.objects.create(
            user=request.user, policy=ConsentPolicy.THRIVE_MARKETING_POLICY, decision=decision
        )
        logger.info(
            "Marketing consent decision updated",
            extra={
                "user_id": request.user.id,
                "consent_id": consent.id,
                "decision": consent.decision,
            },
        )
        messages.add_message(request, messages.SUCCESS, "Your decision has been recorded.")

        # If this is an htmx request, return a single OOB message element
        if request.headers.get("HX-Request") == "true":
            return render(request, "partials/messages.html", {"messages": get_messages(request)})

    return render(request, "users/account_notifications.html", {"decision": decision})
