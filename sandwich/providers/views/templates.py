import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.http import require_POST
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

    return render(
        request,
        "provider/form_list.html",
        {
            "organization": organization,
            "forms": forms_page,
            "form_builder_enabled": settings.FEATURE_PROVIDER_FORM_BUILDER,
        },
    )


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
    if not settings.FEATURE_PROVIDER_FORM_BUILDER:
        logger.info(
            "Form builder feature is disabled, redirecting to form list",
            extra={"user_id": request.user.id, "organization_id": organization.id},
        )
        return redirect("providers:form_templates_list", organization_id=organization.id)

    logger.info(
        "Accessing organization form builder page",
        extra={"user_id": request.user.id, "organization_id": organization.id},
    )
    return render(request, "provider/form_builder.html", {"organization": organization})


@login_required
@require_POST
@authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization", "create_form"])])
def form_file_upload(request: AuthenticatedHttpRequest, organization: Organization):
    """Provider API endpoint to upload a file and generate a form schema."""
    file = request.FILES.get("file")
    if not file:
        return HttpResponseBadRequest("No file uploaded")

    # For now return a simple hardcoded schema as a demo/stub.
    schema = {
        "title": "Sir Galahad the Pure",
        "pages": [
            {
                "name": "page1",
                "elements": [{"type": "text", "name": "q1", "title": "What is your favourite colour?"}],
            }
        ],
    }

    if file.content_type == "application/pdf":
        # TODO(JL): Integrate with LLM to extract schema from PDF content.
        schema["title"] = f"{schema['title']} (from PDF)"
    if file.content_type == "text/csv":
        # TODO(JL): Integrate with LLM to extract schema from CSV content.
        schema["title"] = f"{schema['title']} (from CSV)"

    # form_name = str(schema.get("title", "Untitled Form"))
    # form = Form.objects.create(
    #     organization=organization,
    #     name=form_name,
    #     schema=schema,
    # )

    # Return raw JSON so the existing #form_schema content can
    # be updated via HTMX.
    return JsonResponse(schema)
