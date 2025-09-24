import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from sandwich.core.service.organization_service import get_provider_organizations
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


@login_required
def home(request: AuthenticatedHttpRequest) -> HttpResponse:
    logger.info("Provider accessing home page", extra={"user_id": request.user.id})

    organizations = get_provider_organizations(request.user)
    logger.debug(
        "Retrieved provider organizations",
        extra={"user_id": request.user.id, "organization_count": organizations.count()},
    )

    return render(request, "provider/home.html", {"organizations": organizations})


@login_required
def organization_home(request: AuthenticatedHttpRequest, organization_id: int) -> HttpResponse:
    logger.info("Accessing organization home", extra={"user_id": request.user.id, "organization_id": organization_id})

    organization = get_object_or_404(get_provider_organizations(request.user), id=organization_id)
    logger.debug(
        "Organization home loaded successfully", extra={"user_id": request.user.id, "organization_id": organization_id}
    )

    context = {"organization": organization}
    return render(request, "provider/organization_home.html", context)
