from django.conf import settings
from django.http import HttpRequest

from sandwich.core.models import Organization
from sandwich.core.service.organization_service import get_provider_organizations
from sandwich.core.types import DJANGO_DATE_FORMAT
from sandwich.core.types import DJANGO_DATE_TIME_FORMAT
from sandwich.core.types import EMPTY_VALUE_DISPLAY


def settings_context(request: HttpRequest):
    """Returns context variables from settings."""
    return {
        "datadog_vars": {
            "environment": getattr(settings, "ENVIRONMENT", None),
            "app_version": getattr(settings, "APP_VERSION", None),
            "user_id": request.user.id,
        },
        "EMPTY_VALUE_DISPLAY": EMPTY_VALUE_DISPLAY,
        "DJANGO_DATE_FORMAT": DJANGO_DATE_FORMAT,
        "DJANGO_DATE_TIME_FORMAT": DJANGO_DATE_TIME_FORMAT,
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

    organizations = list(get_provider_organizations(request.user))
    return {
        "user_organizations": organizations,
        "active_organization": _get_active_organization(organizations, request.session.get("active_organization_id")),
    }


def _get_active_organization(organizations: list[Organization], organization_id: str | None) -> Organization | None:
    if not organization_id:
        return None
    for organization in organizations:
        if str(organization_id) == str(organization.id):
            return organization
    return None
