from django.contrib import admin

from sandwich.core.models import Fact


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
