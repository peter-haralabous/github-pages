import logging
from http import HTTPStatus

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.paginator import Paginator
from django.core.validators import FileExtensionValidator
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET
from guardian.shortcuts import get_objects_for_user

from sandwich.core.decorators import surveyjs_csp
from sandwich.core.models import Form
from sandwich.core.models import Organization
from sandwich.core.service.form_generation.generate_form import generate_form_schema_from_reference_file
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


class UploadReferenceForm(forms.Form):
    file = forms.FileField(
        required=True,
        label="Upload File",
        help_text="Upload a file to generate a form schema.",
        widget=forms.FileInput(attrs={"accept": "application/pdf, text/csv", "class": "file-input"}),
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "csv"])],
    )
    description = forms.CharField(
        required=False,
        label="Description",
        widget=forms.Textarea(attrs={"placeholder": "e.g., This is a pre-operative patient intake form..."}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {"hx-target": "#generate-form-modal", "hx-swap": "outerHTML"}
        self.helper.add_input(Submit("upload", "Upload"))


@require_GET
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
            "ai_form_generation_enabled": settings.FEATURE_PROVIDER_AI_FORM_GENERATION,
        },
    )


@require_GET
@login_required
@authorize_objects(
    [
        ObjPerm(Organization, "organization_id", ["view_organization"]),
        ObjPerm(Form, "form_id", ["view_form"]),
    ]
)
def form_template_preview(
    request: AuthenticatedHttpRequest, organization: Organization, form: Form, form_version_id: int
):
    """
    Displays a preview for a from version of a form template
    """

    logger.info(
        "Accessing preview for specific form version",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "form_id": form.id,
            "form_version_pgh_id": form_version_id,
        },
    )
    form_version = form.get_version(form_version_id)
    form_schema = form_version.schema if form_version.schema else {}

    return render(
        request, "provider/form_preview.html", {"organization": organization, "form": form, "form_schema": form_schema}
    )


@require_GET
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


@require_GET
@surveyjs_csp
@login_required
@authorize_objects(
    [
        ObjPerm(Organization, "organization_id", ["view_organization", "create_form"]),
        ObjPerm(Form, "form_id", ["view_form", "change_form"]),
    ]
)
def form_edit(request: AuthenticatedHttpRequest, organization: Organization, form: Form):
    """Provider view to edit an existing form template manually."""
    logger.info(
        "Accessing organization form edit page",
        extra={"user_id": request.user.id, "organization_id": organization.id, "form_id": form.id},
    )
    url = reverse("providers:providers-api:save_form", kwargs={"organization_id": organization.id})
    success_redirect_url = reverse("providers:form_templates_list", kwargs={"organization_id": organization.id})
    return render(
        request,
        "provider/form_builder.html",
        {"organization": organization, "form": form, "form_save_url": url, "success_url": success_redirect_url},
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
    url = reverse("providers:providers-api:save_form", kwargs={"organization_id": organization.id})
    success_redirect_url = reverse("providers:form_templates_list", kwargs={"organization_id": organization.id})
    return render(
        request,
        "provider/form_builder.html",
        {"organization": organization, "form_save_url": url, "success_url": success_redirect_url},
    )


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization", "create_form"])])
def form_file_upload(request: AuthenticatedHttpRequest, organization: Organization):
    """Provider API endpoint to upload a file and generate a form schema."""

    if request.method == "POST":
        upload_reference_form = UploadReferenceForm(request.POST, request.FILES)
        form_post_url = reverse("providers:form_file_upload", kwargs={"organization_id": organization.id})
        upload_reference_form.helper.form_action = form_post_url
        upload_reference_form.helper.attrs = {**upload_reference_form.helper.attrs, "hx-post": form_post_url}

        if upload_reference_form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Form upload successful, processing document.")
            reference_file = upload_reference_form.cleaned_data.get("file")
            assert isinstance(reference_file, InMemoryUploadedFile)
            assert reference_file.name, "Uploaded file has no name"

            form_title = reference_file.name.split(".")[0]
            form = Form.objects.create(
                name=form_title,  # placeholder title
                organization=organization,
                reference_file=reference_file,
            )
            generate_form_schema_from_reference_file.defer(form_id=str(form.id))

            res = HttpResponse(status=HTTPStatus.OK)
            res["HX-Redirect"] = reverse("providers:form_templates_list", kwargs={"organization_id": organization.id})
            return res
    else:
        upload_reference_form = UploadReferenceForm()
        form_post_url = reverse("providers:form_file_upload", kwargs={"organization_id": organization.id})
        upload_reference_form.helper.form_action = form_post_url
        upload_reference_form.helper.attrs = {**upload_reference_form.helper.attrs, "hx-post": form_post_url}

    if request.headers.get("HX-Request") == "true":
        return render(request, "provider/partials/generate_form_modal.html", {"form": upload_reference_form})
    # When the request isn't coming from htmx (refreshes and direct routing)
    # redirect to parent page.
    return redirect(reverse("providers:form_templates_list", kwargs={"organization_id": organization.id}))
