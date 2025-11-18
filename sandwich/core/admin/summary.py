from django.contrib import admin
from django.utils.html import format_html

from sandwich.core.models import Summary


@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    list_display = ("title", "patient", "organization", "status", "template", "created_at")
    search_fields = ("title", "patient__first_name", "patient__last_name", "body")
    list_filter = ("status", "organization__slug", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at", "status_badge")

    fieldsets = (
        (None, {"fields": ("title", "patient", "organization", "status_badge", "status")}),
        ("Relationships", {"fields": ("template", "submission", "encounter")}),
        ("Content", {"fields": ("body",)}),
        ("Metadata", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Status")
    def status_badge(self, obj):
        """Display status with colored badge."""
        colors = {
            "pending": "gray",
            "processing": "blue",
            "succeeded": "green",
            "failed": "red",
        }
        color = colors.get(obj.status.value, "gray")
        return format_html(
            '<span style="padding: 3px 10px; background-color: {}; color: white; border-radius: 3px;">{}</span>',
            color,
            obj.status.label,
        )
