# ruff: noqa: E402, PLC0415
import logging

logger = logging.getLogger(__name__)


def update_env_from_ssm() -> None:
    """
    Pulls params directly from SSM for local development. Ensure aws cli is
    properly configured.
    """
    import os

    import boto3
    from botocore.exceptions import NoRegionError

    params = {
        "GOOGLE_OAUTH_CLIENT_ID": "/integration/sandwich/google_oauth_client_id",
        "GOOGLE_OAUTH_SECRET": "/integration/sandwich/google_oauth_secret",
    }

    try:
        client = boto3.client("ssm")
        for env_var, ssm_param in params.items():
            try:
                res = client.get_parameter(Name=ssm_param, WithDecryption=True)
                if value := res.get("Parameter", {}).get("Value"):
                    os.environ[env_var] = value
            except client.exceptions.ParameterNotFound:
                logger.warning("SSM parameter does not exist.", extra={"param_name": ssm_param})
            # Using a bare exception here because failure to fetch SSM params
            # should not prevent us from starting the dev server locally.
            except Exception:  # noqa: BLE001
                logger.warning("Something went wrong trying to fetch SSM param.", extra={"param_name": ssm_param})

    # NB: We log instead of erroring so ci can pass. This is not ideal
    # because these logs get buried during startup.
    except NoRegionError:
        logger.warning("aws cli not properly configured")


update_env_from_ssm()

from .base import *  # noqa: F403
from .base import APPS_DIR
from .base import INSTALLED_APPS
from .base import LOGGING
from .base import MIDDLEWARE
from .base import WEBPACK_LOADER
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True
SERVE_DJDT = True
SERVE_ERROR_VIEWS = True
SERVE_MEDIA = True

ENVIRONMENT = "local"
APP_URL = "http://localhost:3000"
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="g2n23PCiM72wVceP6LghJcR4hDk6gZ2S59JgvOjChO9YSVsWbCiTaMioUtA6UYpF",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]  # noqa: S104

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    },
}

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = "localhost"
# https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = 1025

# runserver
# ------------------------------------------------------------------------------
INSTALLED_APPS = [
    # https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/daphne/
    "daphne",
    # http://whitenoise.evans.io/en/latest/django.html#using-whitenoise-in-development
    "whitenoise.runserver_nostatic",
    *INSTALLED_APPS,
]


# django-debug-toolbar
# ------------------------------------------------------------------------------
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
INSTALLED_APPS += ["debug_toolbar"]
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#middleware
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-config
DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": [
        "debug_toolbar.panels.redirects.RedirectsPanel",
        # Disable profiling panel due to an issue with Python 3.12:
        # https://github.com/jazzband/django-debug-toolbar/issues/1875
        "debug_toolbar.panels.profiling.ProfilingPanel",
    ],
    "SHOW_TEMPLATE_CONTEXT": True,
}
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#internal-ips
INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]

# show debug logs by default for internal code
LOGGING["loggers"]["sandwich"] = {  # type: ignore[index]
    "handlers": ["console"],
    "level": "DEBUG",
    "propagate": False,
}

# django-extensions
# ------------------------------------------------------------------------------
# https://django-extensions.readthedocs.io/en/latest/installation_instructions.html#configuration
INSTALLED_APPS += ["django_extensions"]

# django-webpack-loader
# ------------------------------------------------------------------------------
WEBPACK_LOADER["DEFAULT"]["CACHE"] = not DEBUG

# Your stuff...
# ------------------------------------------------------------------------------
# when running locally, put uploads under ../data/
MEDIA_ROOT = str(APPS_DIR / "../data/media")
PRIVATE_STORAGE_ROOT = str(APPS_DIR / "../data/private-media")
