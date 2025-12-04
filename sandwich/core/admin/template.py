from django.contrib import admin

from sandwich.core.models import Template


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ("slug", "short_description", "organization")
    search_fields = ("slug",)
    list_filter = ("organization__slug",)

    @admin.display(description="Description", boolean=False)
    def short_description(self, obj):
        return obj.description.splitlines()[0] if obj.description else ""
