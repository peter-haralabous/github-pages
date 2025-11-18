from django.contrib import admin

from sandwich.core.models import SummaryTemplate


@admin.register(SummaryTemplate)
class SummaryTemplateAdmin(admin.ModelAdmin):
    PREVIEW_LENGTH = 100

    list_display = ("name", "organization", "form", "created_at", "updated_at")
    search_fields = ("name", "description")
    list_filter = ("organization__slug", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("name", "organization", "form", "description")}),
        ("Template Content", {"fields": ("text",)}),
        ("Metadata", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Template Preview")
    def short_text(self, obj):
        """Show a preview of the template text."""
        if len(obj.text) > self.PREVIEW_LENGTH:
            return obj.text[: self.PREVIEW_LENGTH] + "..."
        return obj.text
