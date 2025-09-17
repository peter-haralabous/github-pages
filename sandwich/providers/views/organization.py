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
    organization = get_object_or_404(get_provider_organizations(request.user), id=organization_id)

    if request.method == "POST":
        form = OrganizationEdit(request.POST, instance=organization)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Organization updated successfully.")
            return HttpResponseRedirect(reverse("providers:organization", kwargs={"organization_id": organization_id}))
    else:
        form = OrganizationEdit(instance=organization)

    context = {"form": form}
    return render(request, "provider/organization_edit.html", context)


@login_required
def organization_add(request: AuthenticatedHttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = OrganizationAdd(request.POST)
        if form.is_valid():
            organization = form.save()
            create_default_roles(organization)
            # FIXME: why does mypy think that `role_set` isn't an Organization field?
            organization.role_set.get(name=RoleName.OWNER).group.user_set.add(request.user)  # type: ignore[attr-defined]

            messages.add_message(request, messages.SUCCESS, "Organization added successfully.")
            return HttpResponseRedirect(reverse("providers:organization", kwargs={"organization_id": organization.id}))
    else:
        form = OrganizationAdd()

    context = {"form": form}
    return render(request, "provider/organization_add.html", context)
