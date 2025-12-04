"""Admin for list view preferences."""

from django.contrib import admin

from sandwich.core.models import ListViewPreference


@admin.register(ListViewPreference)
class ListViewPreferenceAdmin(admin.ModelAdmin):
    """Admin interface for ListViewPreference model."""

    list_display = [
        "organization",
        "user",
        "list_type",
        "scope",
        "items_per_page",
        "created_at",
        "updated_at",
    ]
    list_filter = ["list_type", "scope", "created_at"]
    search_fields = ["organization__name", "user__email", "user__first_name", "user__last_name"]
    readonly_fields = ["created_at", "updated_at"]
    list_select_related = ["organization", "user"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "organization",
                    "user",
                    "scope",
                    "list_type",
                )
            },
        ),
        (
            "Preferences",
            {
                "fields": (
                    "visible_columns",
                    "default_sort",
                    "items_per_page",
                    "saved_filters",
                )
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related("organization", "user")
