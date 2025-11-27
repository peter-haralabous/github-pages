import logging

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div
from crispy_forms.layout import Layout
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_http_methods
from guardian.shortcuts import get_objects_for_user

from sandwich.core.forms import DeleteConfirmationForm
from sandwich.core.models import Form
from sandwich.core.models.organization import Organization
from sandwich.core.models.summary_template import SummaryTemplate
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.service.summary_template_service import assign_default_summarytemplate_permissions
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.core.util.http import htmx_redirect
from sandwich.core.widgets import WysiwygWidget

logger = logging.getLogger(__name__)


class SummaryTemplateFilterForm(forms.Form):
    SORT_CHOICES = [
        ("-created_at", "Newest first"),
        ("created_at", "Oldest first"),
        ("name", "Name (A-Z)"),
        ("-name", "Name (Z-A)"),
        ("-updated_at", "Recently updated"),
        ("updated_at", "Least recently updated"),
    ]

    search = forms.CharField(required=False, max_length=200)
    sort = forms.ChoiceField(choices=SORT_CHOICES, required=False, initial="-created_at")


class SummaryTemplateForm(forms.ModelForm[SummaryTemplate]):
    def __init__(self, *args, organization: Organization, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.organization = organization

        self.fields["form"].queryset = organization.form_set.order_by("name")  # type: ignore[attr-defined]

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div("name", css_class="flex-1"),
                Div("form", css_class="flex-1"),
                css_class="flex gap-4",
            ),
            "description",
            "text",
        )

    class Meta:
        model = SummaryTemplate
        fields = ("name", "description", "text", "form")
        widgets = {
            "text": WysiwygWidget(
                attrs={
                    "placeholder": "Enter template content using Django template syntax with {% ai %} tags...",
                }
            ),
        }

    def clean_text(self) -> str:
        text = self.cleaned_data.get("text", "")

        if not text.strip():
            raise forms.ValidationError("Template content cannot be empty.")

        return text

    def clean_form(self) -> Form | None:
        form = self.cleaned_data.get("form")
        if form and form.organization != self.organization:
            raise forms.ValidationError("Selected form does not belong to this organization.")
        return form

    def clean_name(self) -> str | None:
        name = self.cleaned_data.get("name")
        if not name:
            return name

        qs = SummaryTemplate.objects.filter(organization=self.organization, name=name)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("A template with this name already exists in this organization.")

        return name

    def save(self, commit: bool = True) -> SummaryTemplate:  # noqa: FBT001, FBT002
        template = super().save(commit=False)
        template.organization = self.organization
        if commit:
            template.save()
        return template


def _get_summary_template_list_context(request: AuthenticatedHttpRequest, organization: Organization) -> dict:
    """Get the context for rendering the summary template list."""

    # Permission note: select_related loads forms without explicit permission checks.
    # This is acceptable because both SummaryTemplate and Form use org-level permissions,
    # so users with view_summarytemplate permission will have view_form permission for
    # the same organization. If granular form permissions are added in the future,
    # this will need to be revisited.
    templates = get_objects_for_user(
        request.user,
        ["view_summarytemplate"],
        SummaryTemplate.objects.filter(organization=organization).select_related("form"),
    )

    filter_form = SummaryTemplateFilterForm(request.GET)
    if filter_form.is_valid():
        search_query = filter_form.cleaned_data.get("search", "").strip()
        sort = filter_form.cleaned_data.get("sort") or "-created_at"
    else:
        search_query = ""
        sort = "-created_at"

    if search_query:
        templates = templates.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

    templates = templates.order_by(sort)

    page = request.GET.get("page", 1)
    paginator = Paginator(templates, 25)
    templates_page = paginator.get_page(page)

    return {
        "organization": organization,
        "templates": templates_page,
        "search": search_query,
        "sort": sort,
        "filter_form": filter_form,
    }


@require_GET
@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization"])])
def summary_template_list(request: AuthenticatedHttpRequest, organization: Organization) -> HttpResponse:
    """Provider view of summary templates for an organization."""
    logger.info(
        "Accessing organization summary template list",
        extra={"user_id": request.user.id, "organization_id": organization.id},
    )

    context = _get_summary_template_list_context(request, organization)

    return render(request, "provider/summary_template_list.html", context)


@require_http_methods(["GET", "POST"])
@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["create_summarytemplate"])])
def summary_template_add(request: AuthenticatedHttpRequest, organization: Organization) -> HttpResponse:
    """Provider view to add a new summary template."""
    logger.info(
        "Accessing summary template add page",
        extra={"user_id": request.user.id, "organization_id": organization.id},
    )

    if request.method == "POST":
        logger.info(
            "Processing summary template add form",
            extra={"user_id": request.user.id, "organization_id": organization.id},
        )
        form = SummaryTemplateForm(request.POST, organization=organization)
        if form.is_valid():
            template = form.save()
            assign_default_summarytemplate_permissions(template)
            logger.info(
                "Summary template created successfully",
                extra={
                    "user_id": request.user.id,
                    "organization_id": organization.id,
                    "template_id": template.id,
                },
            )
            messages.add_message(request, messages.SUCCESS, f"Template '{template.name}' created successfully.")
            return HttpResponseRedirect(
                reverse("providers:summary_template_list", kwargs={"organization_id": organization.id})
            )
        logger.warning(
            "Invalid summary template add form",
            extra={
                "user_id": request.user.id,
                "organization_id": organization.id,
                "form_errors": list(form.errors.keys()),
            },
        )
    else:
        logger.debug(
            "Rendering summary template add form",
            extra={"user_id": request.user.id, "organization_id": organization.id},
        )
        form = SummaryTemplateForm(organization=organization)

    return render(
        request,
        "provider/summary_template_add.html",
        {
            "form": form,
            "organization": organization,
        },
    )


@require_http_methods(["GET", "POST"])
@login_required
@authorize_objects(
    [
        ObjPerm(Organization, "organization_id", ["view_organization"]),
        ObjPerm(SummaryTemplate, "template_id", ["view_summarytemplate", "change_summarytemplate"]),
    ]
)
def summary_template_edit(
    request: AuthenticatedHttpRequest, organization: Organization, summarytemplate: SummaryTemplate
) -> HttpResponse:
    """Provider view to edit an existing summary template."""
    template = summarytemplate
    logger.info(
        "Accessing summary template edit page",
        extra={"user_id": request.user.id, "organization_id": organization.id, "template_id": template.id},
    )

    if request.method == "POST":
        logger.info(
            "Processing summary template edit form",
            extra={"user_id": request.user.id, "organization_id": organization.id, "template_id": template.id},
        )
        form = SummaryTemplateForm(request.POST, instance=template, organization=organization)
        if form.is_valid():
            template = form.save()
            logger.info(
                "Summary template updated successfully",
                extra={
                    "user_id": request.user.id,
                    "organization_id": organization.id,
                    "template_id": template.id,
                },
            )
            messages.add_message(request, messages.SUCCESS, f"Template '{template.name}' updated successfully.")
            return HttpResponseRedirect(
                reverse("providers:summary_template_list", kwargs={"organization_id": organization.id})
            )
        logger.warning(
            "Invalid summary template edit form",
            extra={
                "user_id": request.user.id,
                "organization_id": organization.id,
                "template_id": template.id,
                "form_errors": list(form.errors.keys()),
            },
        )
    else:
        logger.debug(
            "Rendering summary template edit form",
            extra={"user_id": request.user.id, "organization_id": organization.id, "template_id": template.id},
        )
        form = SummaryTemplateForm(instance=template, organization=organization)

    return render(
        request,
        "provider/summary_template_edit.html",
        {
            "form": form,
            "organization": organization,
            "template": template,
        },
    )


@require_http_methods(["GET", "POST"])
@login_required
@authorize_objects(
    [
        ObjPerm(Organization, "organization_id", ["view_organization"]),
        ObjPerm(SummaryTemplate, "template_id", ["view_summarytemplate", "delete_summarytemplate"]),
    ]
)
def summary_template_delete(
    request: AuthenticatedHttpRequest, organization: Organization, summarytemplate: SummaryTemplate
) -> HttpResponse:
    """Delete a summary template."""
    template = summarytemplate
    form_action = reverse(
        "providers:summary_template_delete",
        kwargs={"organization_id": organization.id, "template_id": template.id},
    )

    if request.method == "POST":
        logger.info(
            "Processing summary template deletion",
            extra={"user_id": request.user.id, "organization_id": organization.id, "template_id": template.id},
        )
        form = DeleteConfirmationForm(request.POST, form_action=form_action, hx_target="dialog")
        if form.is_valid():
            template_name = template.name
            logger.info(
                "Deleting summary template",
                extra={"organization_id": organization.id, "template_id": template.id},
            )
            template.delete()
            messages.add_message(request, messages.SUCCESS, f"Template '{template_name}' deleted successfully.")
            return htmx_redirect(
                request, reverse("providers:summary_template_list", kwargs={"organization_id": organization.id})
            )

        # Form is invalid - fall through to render with validation errors
        logger.warning(
            "Invalid summary template delete confirmation",
            extra={"user_id": request.user.id, "template_id": template.id},
        )
    else:
        # GET request - create a new form
        form = DeleteConfirmationForm(form_action=form_action, hx_target="dialog")

    modal_context = {"form": form, "template": template, "organization": organization}

    # If it's an HTMX request, render just the modal partial
    if request.headers.get("HX-Request"):
        return render(request, "provider/partials/summary_template_delete_modal.html", modal_context)

    # Otherwise (direct URL access or page refresh), render the full list page with the modal
    context = _get_summary_template_list_context(request, organization)
    context.update(modal_context)
    return render(request, "provider/summary_template_delete.html", context)
