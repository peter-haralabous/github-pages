from django.contrib import admin

from sandwich.core.models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "created_at", "updated_at")
    prepopulated_fields = {"slug": ["name"]}
    search_fields = ("name", "slug")
    list_filter = ("created_at", "updated_at")
