from django.conf import settings
from django.http import HttpRequest

from sandwich.core.service.organization_service import get_provider_organizations


def settings_context(request: HttpRequest):
    """Returns context variables from settings."""
    return {
        "environment": getattr(settings, "ENVIRONMENT", None),
        "app_version": getattr(settings, "APP_VERSION", None),
    }


def patients_context(request: HttpRequest):
    """Attaches all patients for the current user."""

    if not request.user.is_authenticated:
        return {}

    patients = request.user.patient_set.all()
    return {
        "user_patients": list(patients),
    }


def providers_context(request: HttpRequest):
    """Attaches all organizations for the current user."""

    if not request.user.is_authenticated:
        return {}

    organizations = get_provider_organizations(request.user)
    return {
        "user_organizations": list(organizations),
    }
