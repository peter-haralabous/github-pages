"""
With these settings, tests run faster.
"""

import os

# when running in GitHub Actions set up fake AWS credentials
# not doing this locally as devs might want to record vcrpy fixtures using their real credentials
if os.getenv("GITHUB_WORKFLOW"):
    os.environ.setdefault("AWS_DEFAULT_REGION", "ca-central-1")
    os.environ.setdefault("AWS_ACCESS_KEY_ID", "fake")
    os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "fake")

from .base import *  # noqa: F403
from .base import TEMPLATES
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="45aijxUqMNqunOHSOwIZxD1Sb03Sxfogh4WfD9L9k6gYV2Z8FyvaJlgyToTSXGL2",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#test-runner
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# DATABASE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
# https://docs.djangoproject.com/en/dev/topics/testing/overview/#the-test-database
# Django handles the database settings but not the DATABASE_URL env var
DATABASE_URL = "postgres://sandwich:sandwich@localhost:5432/test_sandwich"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# DEBUGGING FOR TEMPLATES
# ------------------------------------------------------------------------------
TEMPLATES[0]["OPTIONS"]["debug"] = True  # type: ignore[index]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "http://media.testserver/"
# django-webpack-loader
# ------------------------------------------------------------------------------
WEBPACK_LOADER["DEFAULT"]["LOADER_CLASS"] = "webpack_loader.loaders.FakeWebpackLoader"  # noqa: F405

# Your stuff...
# ------------------------------------------------------------------------------
