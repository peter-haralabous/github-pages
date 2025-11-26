from urllib.parse import urlencode

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML
from crispy_forms.layout import Field
from crispy_forms.layout import Layout
from crispy_forms.layout import Submit
from django import forms
from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path
from django.urls import reverse
from django.utils.html import format_html

from sandwich.core.admin.summary_template_fixtures import FixtureConfig
from sandwich.core.admin.summary_template_fixtures import create_or_update_demo_fixtures
from sandwich.core.models import Organization
from sandwich.core.models import SummaryTemplate
from sandwich.core.util.http import AuthenticatedHttpRequest

DEMO_FIXTURES: list[FixtureConfig] = [
    {
        "name": "Health History Assessment",
        "description": (
            "Comprehensive pre-admission health assessment with AI analysis, "
            "risk calculations, and detailed medical history formatting"
        ),
        "form_data_file": "form_health_history_demo.json",
        "template_data_file": "summarytemplate_health_history_demo.json",
    },
    {
        "name": "Simple Health History",
        "description": "Simplified health history form and summary template for basic patient information collection",
        "form_data_file": "form_health_history_simple.json",
        "template_data_file": "summarytemplate_health_history_simple.json",
    },
]


class GenerateDemoTemplatesForm(forms.Form):
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        required=True,
        help_text="Organization to create forms and templates for",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout_fields = [
            Field("organization"),
            HTML("<h2>Select Workflows to Create</h2>"),
        ]

        for i, fixture in enumerate(DEMO_FIXTURES):
            field_name = f"fixture_{i}"
            self.fields[field_name] = forms.BooleanField(
                initial=True,
                required=False,
                label=fixture["name"],
                help_text=fixture["description"],
            )
            layout_fields.append(Field(field_name))

        self.helper = FormHelper()
        self.helper.form_class = "aligned"
        self.helper.layout = Layout(*layout_fields)
        self.helper.add_input(Submit("save", "Generate Demo Forms & Templates", css_class="default"))


def generate_demo_templates_view(request: AuthenticatedHttpRequest) -> HttpResponse:
    """View to generate demo forms and summary templates from data files."""
    form = GenerateDemoTemplatesForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        organization = form.cleaned_data["organization"]

        # Collect selected fixtures
        selected_fixtures = []
        for i, fixture in enumerate(DEMO_FIXTURES):
            field_name = f"fixture_{i}"
            if form.cleaned_data.get(field_name):
                selected_fixtures.append(fixture)

        results = create_or_update_demo_fixtures(organization, selected_fixtures)

        total_operations = (
            results["created_forms"]
            + results["updated_forms"]
            + results["created_templates"]
            + results["updated_templates"]
        )

        if total_operations > 0:
            parts = []
            if results["created_forms"] > 0:
                parts.append(f"created {results['created_forms']} form(s)")
            if results["updated_forms"] > 0:
                parts.append(f"updated {results['updated_forms']} form(s)")
            if results["created_templates"] > 0:
                parts.append(f"created {results['created_templates']} template(s)")
            if results["updated_templates"] > 0:
                parts.append(f"updated {results['updated_templates']} template(s)")

            base_url = reverse("admin:core_summarytemplate_changelist")
            query_params = urlencode({"organization__slug": organization.slug})
            org_link = f"{base_url}?{query_params}"
            message = f"Successfully {', '.join(parts)} for <a href='{org_link}'>{organization.slug}</a>"
            messages.success(request, format_html(message))

        for error in results["errors"]:
            messages.error(request, error)

        return HttpResponseRedirect(reverse("admin:core_summarytemplate_changelist"))

    return TemplateResponse(
        request,
        "admin/core/summarytemplate/generate_demo_templates.html",
        {
            "form": form,
            "fixtures": DEMO_FIXTURES,
            "title": "Generate Demo Forms & Templates",
        },
    )


@admin.register(SummaryTemplate)
class SummaryTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "form", "created_at", "updated_at")
    search_fields = ("name", "description")
    list_filter = ("organization__slug", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    actions = ["duplicate_templates"]

    fieldsets = (
        (None, {"fields": ("name", "organization", "form", "description")}),
        (
            "Template Content",
            {
                "fields": ("text",),
            },
        ),
        ("Metadata", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_urls(self):
        return [
            path(
                "generate_demo_templates/",
                self.admin_site.admin_view(generate_demo_templates_view),
                name="generate_demo_summary_templates",
            ),
            *super().get_urls(),
        ]

    @admin.action(description="Duplicate selected templates")
    def duplicate_templates(self, request, queryset):
        count = 0
        for template in queryset:
            # Create a copy with a modified name
            new_name = f"{template.name} (Copy)"
            # Make sure the name is unique
            counter = 1
            while SummaryTemplate.objects.filter(organization=template.organization, name=new_name).exists():
                new_name = f"{template.name} (Copy {counter})"
                counter += 1

            SummaryTemplate.objects.create(
                organization=template.organization,
                form=template.form,
                name=new_name,
                description=template.description,
                text=template.text,
            )
            count += 1

        messages.success(request, f"Successfully duplicated {count} template(s)")

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["show_demo_button"] = True
        extra_context["demo_url"] = reverse("admin:generate_demo_summary_templates")
        return super().changelist_view(request, extra_context)
