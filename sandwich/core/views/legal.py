import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from sandwich.core.models import Consent
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


@login_required
def legal_view(request: AuthenticatedHttpRequest) -> HttpResponse:
    consents = Consent.objects.for_user(request.user)

    if len(consents) == 0:
        logger.critical("User has no consented policies", extra={"user_id": request.user.pk})

    return render(
        request,
        "users/legal.html",
        {
            "consents": consents,
        },
    )
