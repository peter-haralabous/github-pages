import logging
from datetime import date
from http import HTTPStatus

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
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
from sandwich.core.models.form import FormStatus
from sandwich.core.service.form_generation.generate_form import generate_form_schema
from sandwich.core.service.form_service import assign_default_form_permissions
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


class UploadReferenceForm(forms.Form):
    name = forms.CharField(
        label="Form Name",
        required=True,
        widget=forms.TextInput(),
    )
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
    organization_forms = (
        Form.objects.filter(organization=organization).exclude(status=FormStatus.FAILED).order_by("-created_at")
    )
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
        },
    )


@login_required
@authorize_objects(
    [
        ObjPerm(Organization, "organization_id", ["view_organization"]),
        ObjPerm(Form, "form_id", ["change_form"]),
    ]
)
def form_template_restore(
    request: AuthenticatedHttpRequest, organization: Organization, form: Form, form_version_id: int
):
    """
    Restores a form version to make it the current form
    """

    if request.method == "POST":
        logger.info(
            "Restoring a form version of a specific form",
            extra={
                "user_id": request.user.id,
                "organization_id": organization.id,
                "form_id": form.id,
                "form_version_pgh_id": form_version_id,
            },
        )

        form.restore_to(form_version_id)

        return redirect(
            reverse("providers:form_template", kwargs={"organization_id": organization.id, "form_id": form.id})
        )

    version_number = request.GET.get("version_number")
    modal_context = {
        "form": form,
        "organization": organization,
        "form_version_id": form_version_id,
        "version_number": version_number,
    }

    return render(request, "provider/partials/restore_form_template_modal.html", modal_context)


@require_GET
@login_required
@surveyjs_csp
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
    return render(
        request,
        "provider/form_builder.html",
        {"organization": organization, "form": form, "form_save_url": url},
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

    form = Form.objects.create(organization=organization, name=f"unnamed form created on {date.today().isoformat()}")  # noqa: DTZ011

    return redirect(
        reverse("providers:form_template_edit", kwargs={"organization_id": organization.id, "form_id": form.id})
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
            form_name = upload_reference_form.cleaned_data.get("name")
            reference_file = upload_reference_form.cleaned_data.get("file")
            assert isinstance(reference_file, InMemoryUploadedFile)
            assert reference_file.name, "Uploaded file has no name"

            form, created = Form.objects.get_or_create(
                name=form_name,
                organization=organization,
                defaults={
                    "status": FormStatus.GENERATING,
                    "reference_file": reference_file,
                    "schema": {"title": form_name},
                },
            )
            if created:
                assign_default_form_permissions(form)
                generate_form_schema.defer(form_id=str(form.id))
                res = HttpResponse(status=HTTPStatus.OK)

                res["HX-Redirect"] = reverse(
                    "providers:form_templates_list", kwargs={"organization_id": organization.id}
                )
                return res

            upload_reference_form.add_error("title", "A form with this title already exists.")

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
