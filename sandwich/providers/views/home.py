from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from sandwich.core.service.organization_service import get_provider_organizations
from sandwich.core.util.http import AuthenticatedHttpRequest


@login_required
def home(request: AuthenticatedHttpRequest) -> HttpResponse:
    organizations = get_provider_organizations(request.user)
    return render(request, "provider/home.html", {"organizations": organizations})


@login_required
def organization_home(request: AuthenticatedHttpRequest, organization_id: int) -> HttpResponse:
    organization = get_object_or_404(get_provider_organizations(request.user), id=organization_id)
    return render(request, "provider/organization_home.html", {"organization": organization})
