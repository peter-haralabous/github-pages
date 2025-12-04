from django.contrib import admin

from sandwich.core.models import Predicate


@admin.register(Predicate)
class PredicateAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name", "description")
    list_filter = ("name",)
    ordering = ("id",)
    readonly_fields = ("id",)
