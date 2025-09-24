import logging

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse

from sandwich.core.models.organization import Organization
from sandwich.core.models.role import RoleName
from sandwich.core.service.organization_service import create_default_roles
from sandwich.core.service.organization_service import get_provider_organizations
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


class OrganizationEdit(forms.ModelForm[Organization]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit"))

    class Meta:
        model = Organization
        fields = ("name", "patient_statuses")


class OrganizationAdd(forms.ModelForm[Organization]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit"))

    class Meta:
        model = Organization
        fields = ("name", "patient_statuses")


@login_required
def organization_edit(request: AuthenticatedHttpRequest, organization_id: int) -> HttpResponse:
    logger.info("Accessing organization edit", extra={"user_id": request.user.id, "organization_id": organization_id})

    organization = get_object_or_404(get_provider_organizations(request.user), id=organization_id)

    if request.method == "POST":
        logger.info(
            "Processing organization edit form", extra={"user_id": request.user.id, "organization_id": organization_id}
        )
        form = OrganizationEdit(request.POST, instance=organization)
        if form.is_valid():
            form.save()
            logger.info(
                "Organization updated successfully",
                extra={"user_id": request.user.id, "organization_id": organization_id},
            )
            messages.add_message(request, messages.SUCCESS, "Organization updated successfully.")
            return HttpResponseRedirect(reverse("providers:organization", kwargs={"organization_id": organization_id}))
        logger.warning(
            "Invalid organization edit form",
            extra={
                "user_id": request.user.id,
                "organization_id": organization_id,
                "form_errors": list(form.errors.keys()),
            },
        )
    else:
        logger.debug(
            "Rendering organization edit form", extra={"user_id": request.user.id, "organization_id": organization_id}
        )
        form = OrganizationEdit(instance=organization)

    context = {"form": form}
    return render(request, "provider/organization_edit.html", context)


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
            create_default_roles(organization)
            # FIXME: why does mypy think that `role_set` isn't an Organization field?
            organization.role_set.get(name=RoleName.OWNER).group.user_set.add(request.user)  # type: ignore[attr-defined]
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
