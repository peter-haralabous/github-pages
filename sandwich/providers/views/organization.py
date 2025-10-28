import logging

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from csp.constants import UNSAFE_INLINE
from csp.decorators import csp_update
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django_jsonform.widgets import JSONFormWidget
from django_pydantic_field.forms import SchemaField

from sandwich.core.forms import DeleteConfirmationForm
from sandwich.core.models.organization import Organization
from sandwich.core.models.organization import PatientStatus
from sandwich.core.models.role import RoleName
from sandwich.core.service.organization_service import assign_organization_role
from sandwich.core.service.organization_service import create_default_roles_and_perms
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


class OrganizationEdit(forms.ModelForm[Organization]):
    patient_statuses = SchemaField(schema=list[PatientStatus], widget=JSONFormWidget, required=False)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit"))

    class Meta:
        model = Organization
        fields = ("name", "patient_statuses", "verification_type")


class OrganizationAdd(forms.ModelForm[Organization]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit"))

    class Meta:
        model = Organization
        fields = ("name",)


# The JSONFormWidget for PatientStatuses uses this method for style
@csp_update({"style-src-attr": UNSAFE_INLINE})
@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization", "change_organization"])])
def organization_edit(request: AuthenticatedHttpRequest, organization: Organization) -> HttpResponse:
    logger.info("Accessing organization edit", extra={"user_id": request.user.id, "organization_id": organization.id})

    if request.method == "POST":
        logger.info(
            "Processing organization edit form", extra={"user_id": request.user.id, "organization_id": organization.id}
        )
        form = OrganizationEdit(request.POST, instance=organization)
        if form.is_valid():
            form.save()
            logger.info(
                "Organization updated successfully",
                extra={"user_id": request.user.id, "organization_id": organization.id},
            )
            messages.add_message(request, messages.SUCCESS, "Organization updated successfully.")
            return HttpResponseRedirect(
                reverse("providers:organization_edit", kwargs={"organization_id": organization.id})
            )
        logger.warning(
            "Invalid organization edit form",
            extra={
                "user_id": request.user.id,
                "organization_id": organization.id,
                "form_errors": list(form.errors.keys()),
            },
        )
    else:
        logger.debug(
            "Rendering organization edit form", extra={"user_id": request.user.id, "organization_id": organization.id}
        )
        form = OrganizationEdit(instance=organization)

    context = {
        "form": form,
        "organization": organization,
    }
    return render(request, "provider/organization_edit.html", context)


# TODO(MM): Add permissions -- for now we'll leave this unchecked so any role
# can create an org to test
@login_required
def organization_add(request: AuthenticatedHttpRequest) -> HttpResponse:
    logger.info("Accessing organization add", extra={"user_id": request.user.id})

    if request.method == "POST":
        logger.info("Processing organization add form", extra={"user_id": request.user.id})
        form = OrganizationAdd(request.POST)
        if form.is_valid():
            organization = form.save()
            logger.info(
                "Organization created successfully",
                extra={"user_id": request.user.id, "organization_id": organization.id},
            )
            # Note: form.save() does not call the create method for the
            # associated model. This means we need to explicitly call
            # create_default_roles_and_perms.
            create_default_roles_and_perms(organization)
            assign_organization_role(organization, RoleName.OWNER, request.user)
            logger.debug(
                "User assigned as organization owner",
                extra={"user_id": request.user.id, "organization_id": organization.id},
            )

            messages.add_message(request, messages.SUCCESS, "Organization added successfully.")
            return HttpResponseRedirect(reverse("providers:organization", kwargs={"organization_id": organization.id}))
        logger.warning(
            "Invalid organization add form",
            extra={"user_id": request.user.id, "form_errors": list(form.errors.keys())},
        )
    else:
        logger.debug("Rendering organization add form", extra={"user_id": request.user.id})
        form = OrganizationAdd()

    context = {"form": form}
    return render(request, "provider/organization_add.html", context)


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization", "delete_organization"])])
def organization_delete(request: AuthenticatedHttpRequest, organization: Organization) -> HttpResponse:
    if request.method == "POST":
        logger.info("Processing organization deletion", extra={"user_id": request.user.id})
        form = DeleteConfirmationForm(request.POST)
        if form.is_valid():
            org = Organization.objects.get(id=str(organization.id))
            logger.info("Deleting organization", extra={"org_id": org.id})
            org.delete()
            return redirect(reverse("providers:home"))

    form = DeleteConfirmationForm(
        form_action=reverse("providers:organization_delete", kwargs={"organization_id": organization.id})
    )
    context = {"form": form}
    return render(request, "provider/partials/organization_delete_modal.html", context)
