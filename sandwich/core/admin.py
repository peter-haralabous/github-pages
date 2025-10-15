from django.contrib import admin

from sandwich.core.models import Consent
from sandwich.core.models import Document
from sandwich.core.models import Email
from sandwich.core.models import Encounter
from sandwich.core.models import FormioSubmission
from sandwich.core.models import Invitation
from sandwich.core.models import Organization
from sandwich.core.models import Patient
from sandwich.core.models import Task
from sandwich.core.models import Template


@admin.register(Consent)
class ConsentAdmin(admin.ModelAdmin):
    list_display = ("user", "policy", "decision")
    search_fields = ("user__email", "policy")
    list_filter = ("policy", "decision", "created_at", "updated_at")


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ("to", "status", "created_at", "updated_at")
    search_fields = ("to",)
    list_filter = ("status", "created_at", "updated_at")


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "created_at", "updated_at")
    prepopulated_fields = {"slug": ["name"]}
    search_fields = ("name", "slug")
    list_filter = ("created_at", "updated_at")


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ("slug", "short_description", "organization")
    search_fields = ("slug",)
    list_filter = ("organization__slug",)

    @admin.display(description="Description", boolean=False)
    def short_description(self, obj):
        return obj.description.splitlines()[0] if obj.description else ""


admin.site.register(
    [Document, Encounter, FormioSubmission, Invitation, Patient, Task],
)
