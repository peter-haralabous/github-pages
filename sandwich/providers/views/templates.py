import logging

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from guardian.shortcuts import get_objects_for_user

from sandwich.core.decorators import surveyjs_csp
from sandwich.core.models import Form
from sandwich.core.models import Organization
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization"])])
def form_list(request: AuthenticatedHttpRequest, organization: Organization):
    """Provider view of form templates for an organization.

    Displays the list of available forms for the organization.
    """
    logger.info(
        "Accessing organization form list",
        extra={"user_id": request.user.id, "organization_id": organization.id},
    )
    organization_forms = Form.objects.filter(organization=organization).order_by("name")
    authorized_org_forms = get_objects_for_user(request.user, ["view_form"], organization_forms)

    page = request.GET.get("page", 1)
    paginator = Paginator(authorized_org_forms, 25)
    forms_page = paginator.get_page(page)

    return render(request, "provider/form_list.html", {"organization": organization, "forms": forms_page})


@login_required
@authorize_objects(
    [
        ObjPerm(Organization, "organization_id", ["view_organization"]),
        ObjPerm(Form, "form_id", ["view_form"]),
    ]
)
def form_details(request: AuthenticatedHttpRequest, organization: Organization, form: Form):
    """Provider view of a single form template.

    Displays the list of form versions.
    """
    logger.info(
        "Accessing organization form details with version history",
        extra={"user_id": request.user.id, "organization_id": organization.id, "form_id": form.id},
    )
    # If a user has view_form permissions, this includes the ability to see its version history.
    form_versions = form.get_versions()

    return render(
        request, "provider/form_details.html", {"organization": organization, "form": form, "forms": form_versions}
    )


@surveyjs_csp
@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization", "create_form"])])
def form_builder(request: AuthenticatedHttpRequest, organization: Organization):
    """Provider view to create a new form template manually."""
    logger.info(
        "Accessing organization form builder page",
        extra={"user_id": request.user.id, "organization_id": organization.id},
    )
    return render(request, "provider/form_builder.html", {"organization": organization})
