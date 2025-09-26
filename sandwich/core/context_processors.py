from django.conf import settings


def settings_context(request):
    """Returns context variables from settings."""
    return {
        "environment": getattr(settings, "ENVIRONMENT", None),
        "app_version": getattr(settings, "APP_VERSION", None),
    }
