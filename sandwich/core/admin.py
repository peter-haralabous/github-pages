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
from sandwich.core.models.entity import Entity
from sandwich.core.models.fact import Fact
from sandwich.core.models.predicate import Predicate


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


@admin.register(Fact)
class FactAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("subject", "predicate", "object", "provenance")}),
        ("Metadata", {"fields": ("metadata",)}),
        ("Dates", {"fields": ("start_datetime", "end_datetime")}),
    )
    list_display = ["id", "subject", "predicate", "object", "start_datetime", "end_datetime"]
    search_fields = ["subject__id", "object__id", "predicate__name"]
    ordering = ["-start_datetime"]
    readonly_fields = ["id"]


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "metadata")
    search_fields = ("id", "type")
    list_filter = ("type",)
    ordering = ("id",)
    readonly_fields = ("id",)


@admin.register(Predicate)
class PredicateAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name", "description")
    list_filter = ("name",)
    ordering = ("id",)
    readonly_fields = ("id",)


admin.site.register(
    [Document, Encounter, FormioSubmission, Invitation, Patient, Task],
)
