from django.contrib import admin

from sandwich.core.models import Consent


@admin.register(Consent)
class ConsentAdmin(admin.ModelAdmin):
    list_display = ("user", "policy", "decision")
    search_fields = ("user__email", "policy")
    list_filter = ("policy", "decision", "created_at", "updated_at")
