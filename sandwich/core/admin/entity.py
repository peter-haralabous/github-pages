from django.contrib import admin

from sandwich.core.models import Entity


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "metadata")
    search_fields = ("id", "type")
    list_filter = ("type",)
    ordering = ("id",)
    readonly_fields = ("id",)
