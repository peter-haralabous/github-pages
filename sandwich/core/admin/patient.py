from django.contrib import admin

from sandwich.core.models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "organization_id", "user_id")
