import logging

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from sandwich.core.models import Form
from sandwich.core.models import Organization
from sandwich.core.service.organization_service import get_provider_organizations
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization"])])
def templates_home(request: AuthenticatedHttpRequest, organization: Organization):
    """Provider template landing page to choose to manage form or summary templates."""
    logger.info(
        "Accessing organization templates", extra={"user_id": request.user.id, "organization_id": organization.id}
    )
    return render(request, "provider/templates.html", {"organization": organization})


# TODO: Permissions
@login_required
def form_list(request: AuthenticatedHttpRequest, organization_id: int):
    """Provider view of form templates for an organization.

    Displays the list of available forms for the organization.
    """
    logger.info(
        "Accessing organization form list",
        extra={"user_id": request.user.id, "organization_id": organization_id},
    )
    organization = get_object_or_404(get_provider_organizations(request.user), id=organization_id)
    forms = Form.objects.filter(organization=organization)

    page = request.GET.get("page", 1)
    paginator = Paginator(forms, 25)
    forms_page = paginator.get_page(page)

    return render(request, "provider/form_list.html", {"organization": organization, "forms": forms_page})
