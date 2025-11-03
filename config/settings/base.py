"""Base settings to build other settings files upon."""

from pathlib import Path
from urllib.parse import quote_plus
from urllib.parse import urlencode

import django_stubs_ext
import environ
from allauth.socialaccount.providers.patreon.constants import API_VERSION
from csp.constants import NONCE
from csp.constants import SELF
from csp.constants import UNSAFE_HASHES

django_stubs_ext.monkeypatch()

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
# sandwich/
APPS_DIR = BASE_DIR / "sandwich"
env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(BASE_DIR / ".env"))

# GENERAL
# ------------------------------------------------------------------------------
ENVIRONMENT = env.str("ENVIRONMENT_NAME", default="not set")
APP_URL = env.str(
    "APP_URL", default={"integration": "https://hc.wethrive.ninja"}.get(ENVIRONMENT, "https://hc.thrive.health")
)
APP_VERSION = env.str("APP_VERSION", default="latest")
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = "UTC"
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "en-ca"
# https://docs.djangoproject.com/en/dev/ref/settings/#languages
# from django.utils.translation import gettext_lazy as _
LANGUAGES = [
    ("en-ca", "English"),
    ("fr-ca", "French"),
]
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
# https://docs.djangoproject.com/en/dev/ref/settings/#locale-paths
LOCALE_PATHS = [str(BASE_DIR / "locale")]

# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
# To configure the Procrastinate app, need the db connection string.
DATABASE_URL = env.str("DATABASE_URL", default="postgres://sandwich:sandwich@localhost:5432/sandwich")
DATABASES = {"default": env.db_url_config(DATABASE_URL)}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DJANGO_CONN_MAX_AGE", default=60)
DATABASES["default"]["ATOMIC_REQUESTS"] = True
# https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-DEFAULT_AUTO_FIELD
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

SERVE_DJDT = env.bool("DJANGO_SERVE_DJDT", default=DEBUG)
SERVE_ERROR_VIEWS = env.bool("DJANGO_SERVE_ERROR_VIEWS", default=DEBUG)
SERVE_MEDIA = env.bool("DJANGO_SERVE_MEDIA", default=DEBUG)

# APPS
# ------------------------------------------------------------------------------
PRIORITY_APPS = [
    "modeltranslation",  # < django.contrib.admin
    "pghistory.admin",
]
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "django.contrib.humanize", # Handy template tags
    "django.contrib.admin",
    "django.forms",
]
THIRD_PARTY_APPS = [
    "crispy_forms",
    "crispy_tailwind",
    "allauth",
    "allauth.account",
    "allauth.mfa",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "csp",
    "webpack_loader",
    "django_jsonform",
    "procrastinate.contrib.django",
    "private_storage",
    "guardian",
    "lucide",
    "django_eventstream",
    "pghistory",
    "pgtrigger",
]

LOCAL_APPS = [
    "sandwich.users",
    "sandwich.core",
    "sandwich.patients",
    "sandwich.providers",
    # Your stuff: custom apps go here
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = PRIORITY_APPS + DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
    "guardian.backends.ObjectPermissionBackend",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = "users.User"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = "users:redirect"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = "account_login"

# Google OAuth
# When run locally, these envs get set by `settings/local.py`
GOOGLE_OAUTH_CLIENT_ID = env.str("GOOGLE_OAUTH_CLIENT_ID", default=None)
GOOGLE_OAUTH_SECRET = env.str("GOOGLE_OAUTH_SECRET", default=None)

# https://docs.allauth.org/en/dev/socialaccount/configuration.html
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

if GOOGLE_OAUTH_SECRET and GOOGLE_OAUTH_CLIENT_ID:
    SOCIALACCOUNT_PROVIDERS = {
        "google": {
            "APPS": [
                {
                    "client_id": GOOGLE_OAUTH_CLIENT_ID,
                    "secret": GOOGLE_OAUTH_SECRET,
                    "key": "",
                    "settings": {
                        "scope": [
                            "profile",
                            "email",
                        ],
                        "auth_params": {
                            "access_type": "online",
                        },
                    },
                },
            ],
            "SCOPE": ["profile", "email"],
            "AUTH_PARAMS": {
                "access_type": "online",
            },
            # This is potentially dangerous when used with untrustworthy
            # providers -- so we apply on a per-provider basis.
            # https://docs.allauth.org/en/dev/socialaccount/configuration.html
            "EMAIL_AUTHENTICATION": True,
        }
    }

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "csp.middleware.CSPMiddleware",
    "pghistory.middleware.HistoryMiddleware",
    "sandwich.core.middleware.TimezoneMiddleware",
    "sandwich.core.middleware.ConsentMiddleware",
    "sandwich.patients.middleware.patient_access.PatientAccessMiddleware",
]

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(BASE_DIR / "staticfiles")
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(APPS_DIR / "static")]
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "sandwich.core.finders.CustomFileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR / "media")
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#dirs
        "DIRS": [str(APPS_DIR / "templates")],
        # https://docs.djangoproject.com/en/dev/ref/settings/#app-dirs
        "APP_DIRS": True,
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "sandwich.core.context_processors.settings_context",
                "sandwich.core.context_processors.patients_context",
                "sandwich.core.context_processors.providers_context",
                "sandwich.core.context_processors.htmx_context",
                "sandwich.core.context_processors.active_organization_context",
                "sandwich.users.context_processors.allauth_settings",
            ],
        },
    },
]

# https://docs.djangoproject.com/en/dev/ref/settings/#form-renderer
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = "tailwind"
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"

# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = (str(APPS_DIR / "fixtures"),)
SERIALIZATION_MODULES = {
    "sandwich": "sandwich.core.serializers.sandwich",
}

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = "DENY"

# https://docs.datadoghq.com/integrations/content_security_policy_logs/?tab=firefox#use-csp-with-real-user-monitoring-and-session-replay
report_params = urlencode(
    {
        # This is a public key, meant to be shared
        "dd-api-key": "pub7f4333094988c697036a7a428df4dcf6",
        "dd-evp-origin": "content-security-policy",
        "ddsource": "csp-report",
    }
)
report_tags = quote_plus(f"service:sandwich,environment:{ENVIRONMENT},version:{API_VERSION}")
rum_host = "https://browser-intake-datadoghq.eu"
report_uri = f"{rum_host}/api/v2/logs?{report_params}&ddtags={report_tags}"
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "connect-src": [SELF, f"{rum_host}/"],
        "default-src": [SELF],
        "frame-ancestors": [SELF],
        "report-uri": report_uri,
        "img-src": [SELF, "data:"],
        "script-src": [SELF, NONCE],
        "script-src-elem": [SELF, NONCE],
        "style-src-elem": [
            SELF,
            NONCE,
            UNSAFE_HASHES,
            "'sha256-faU7yAF8NxuMTNEwVmBz+VcYeIoBQ2EMHW3WaVxCvnk='",  # htmx injects a <style> tag
        ],
        "worker-src": [SELF, "blob:"],
    },
}
# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-timeout
EMAIL_TIMEOUT = 5

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = "admin/"
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [("""Thrive Health""", "dev@thrive.health")]
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
# https://cookiecutter-django.readthedocs.io/en/latest/settings.html#other-environment-settings
# Force the `admin` sign in process to go through the `django-allauth` workflow
DJANGO_ADMIN_FORCE_ALLAUTH = env.bool("DJANGO_ADMIN_FORCE_ALLAUTH", default=False)

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"()": "config.logging.CustomDataDogJSONFormatter"},
        "pretty": {"()": "config.logging.ColorPrettyFormatter"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "filters": {
        "procrastinate": {
            "()": "config.logging.ProcrastinateBlueprintFilter",
            "name": "procrastinate",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
    "loggers": {
        "django": {
            # by default this is ["console", "mail_admins"]; we don't want either.
            # just let everything flow up to the root
            "handlers": [],
        },
        "procrastinate.blueprints": {
            "filters": ["procrastinate"],
        },
    },
}

# pass `extra={}` through to datadog
DJANGO_DATADOG_LOGGER_EXTRA_INCLUDE = r"^(django_datadog_logger|procrastinate|sandwich)(|\..+)$"


# django-allauth
# ------------------------------------------------------------------------------
ACCOUNT_ALLOW_REGISTRATION = env.bool("DJANGO_ACCOUNT_ALLOW_REGISTRATION", True)
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_LOGIN_METHODS = {"email"}
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_ADAPTER = "sandwich.users.adapters.AccountAdapter"
# https://docs.allauth.org/en/latest/account/forms.html
ACCOUNT_FORMS = {"signup": "sandwich.users.forms.UserSignupForm"}
# https://docs.allauth.org/en/latest/socialaccount/configuration.html
SOCIALACCOUNT_ADAPTER = "sandwich.users.adapters.SocialAccountAdapter"
# https://docs.allauth.org/en/latest/socialaccount/configuration.html
SOCIALACCOUNT_FORMS = {"signup": "sandwich.users.forms.UserSocialSignupForm"}


# django-guardian
# ------------------------------------------------------------------------------
GUARDIAN_MONKEY_PATCH_USER = (
    False  # https://django-guardian.readthedocs.io/en/latest/userguide/custom-user-model#custom-user-model
)
GUARDIAN_RAISE_403 = True  # show our styled 403 error page


# django-webpack-loader
# ------------------------------------------------------------------------------
WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": not DEBUG,
        "CSP_NONCE": True,
        "STATS_FILE": BASE_DIR / "webpack-stats.json",
        "POLL_INTERVAL": 0.1,
        "IGNORE": [r".+\.hot-update.js", r".+\.map"],
    },
}

# Your stuff...
# ------------------------------------------------------------------------------

# NOTE-NG: this function guards access to the `/private-media` route, which should only be visible to admins.
#          after adding a PrivateFileField to a model you probably want to create a matching PrivateStorageDetailView
#          that will enforce the relevant object permissions to view that file.
#          see `sandwich.patients.views.document.DocumentDownloadView` for an example.
PRIVATE_STORAGE_AUTH_FUNCTION = "private_storage.permissions.allow_superuser"
PRIVATE_STORAGE_ROOT = str(APPS_DIR / "private-media")

# LLM API keys
# they're all defaulted to None so that tests don't need to mock them eagerly;
# trying to use them will fail at runtime (see sandwich/core/service/llm.py)
GEMINI_API_KEY = env.str("GEMINI_API_KEY", default=None)
BEDROCK_CLAUDE_3_SONNET_ARN = env.str("BEDROCK_CLAUDE_3_SONNET_ARN", default=None)
BEDROCK_CLAUDE_SONNET_4_5_ARN = env.str("BEDROCK_CLAUDE_SONNET_4_5_ARN", default=None)
BEDROCK_GPT_OSS_120B_ARN = env.str("BEDROCK_GPT_OSS_120B_ARN", default=None)

# https://github.com/fanout/django-eventstream
EVENTSTREAM_REDIS = {
    "host": env.str("REDIS_HOST", default="localhost"),
    "port": env.int("REDIS_PORT", default=6379),
    "db": env.int("REDIS_DB", default=0),
    "password": env.str("REDIS_PASSWORD", default=None),
    "ssl": env.bool("REDIS_SSL", default=False),
}
EVENTSTREAM_CHANNELMANAGER_CLASS = "sandwich.core.eventstream.ChannelManager"
