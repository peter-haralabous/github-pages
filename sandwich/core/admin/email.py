from django.contrib import admin

from sandwich.core.models import Email


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ("to", "status", "created_at", "updated_at")
    search_fields = ("to",)
    list_filter = ("status", "created_at", "updated_at")
