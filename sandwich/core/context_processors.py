from django.conf import settings
from django.http import HttpRequest

from sandwich.core.service.organization_service import get_active_organization
from sandwich.core.service.organization_service import get_provider_organizations


def settings_context(request: HttpRequest):
    """Returns context variables from settings."""
    return {
        "environment": getattr(settings, "ENVIRONMENT", None),
        "app_version": getattr(settings, "APP_VERSION", None),
    }


def htmx_context(request: HttpRequest):
    """Make some HTMX headers available to templates."""
    return {
        "hx_request": request.headers.get("HX-Request") == "true",
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


def active_organization_context(request: HttpRequest):
    """Attaches current active organization for the current user."""

    if not request.user.is_authenticated:
        return {}

    active_organization = get_active_organization(request.user, request.session.get("active_organization_id"))
    return {
        "active_organization": active_organization,
    }
