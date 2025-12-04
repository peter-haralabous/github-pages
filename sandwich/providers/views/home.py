import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import resolve_url

from sandwich.core.models.organization import Organization
from sandwich.core.service.organization_service import get_provider_organizations
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
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

    # If the user has only a single organization, shortcut them to their org page.
    # TODO-WF: That means that we'll need to expose a way somewhere else for a single org user to add multiple
    #          orgs (probably though settings page somewhere)
    if organizations.count() == 1:
        if org := organizations.first():
            return redirect(to=resolve_url("providers:organization", organization_id=org.id))

    return render(request, "provider/home.html", {"organizations": organizations})


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization"])])
def organization_home(request: AuthenticatedHttpRequest, organization: Organization) -> HttpResponse:
    """
    Maybe we'll use this page one day, but for now, it's vestigial - all the action happens on the encounters list.
    """
    return redirect(to=resolve_url("providers:encounter_list", organization_id=organization.id))
