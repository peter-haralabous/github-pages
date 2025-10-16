from collections.abc import Callable
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import URLPattern
from django.urls import URLResolver
from django.urls import get_resolver
from django.views.generic import View
from django_extensions.management.commands.show_urls import Command as ShowUrlsCommand
from ninja.operation import PathView


@dataclass
class UrlRegistration:
    name: str
    pattern: str
    view: Callable[..., Any]


def get_all_urls(
    url_patterns: Sequence[URLPattern | URLResolver], base: str = "", namespace: str | None = None
) -> list[UrlRegistration]:
    """
    Recursively explores the URL patterns to generate a flat list of all URLs.
    """
    urls = ShowUrlsCommand().extract_views_from_urlpatterns(url_patterns, base, namespace=namespace)
    # Each object in the returned list is a three-tuple: (view_func, regex, name)
    return [UrlRegistration(name, regex, view) for view, regex, name in urls]


def is_login_required(view_callback):
    """
    Introspects a view callback to determine if it requires login.

    Returns:
        bool: True if login is required, False otherwise.
    """
    # Case 1: django-ninja
    if isinstance(getattr(view_callback, "__self__", None), PathView):
        return all(len(o.auth_callbacks) > 0 for o in view_callback.__self__.operations)

    # Case 2: Class-Based View
    if hasattr(view_callback, "view_class"):
        view_class = view_callback.view_class
        if issubclass(view_class, LoginRequiredMixin):
            return True

    # Case 3: Function-Based View
    # This relies on an implementation detail of the @login_required decorator.
    # It wraps the view in a function that has a 'login_url' attribute.
    # This also detects @permission_required, as it uses the same underlying decorator.
    return hasattr(view_callback, "login_url")


def test_is_login_required():
    class ExampleClassBasedView(View):
        pass

    class ExampleLoginRequiredClassBasedView(LoginRequiredMixin, View):
        pass

    decorated_class_based_view = login_required(ExampleClassBasedView.as_view())

    def function_based_view(request):
        pass

    @login_required
    def decorated_function_based_view(request):
        pass

    assert is_login_required(ExampleClassBasedView.as_view()) is False
    assert is_login_required(ExampleLoginRequiredClassBasedView.as_view()) is True
    assert is_login_required(decorated_class_based_view) is True
    assert is_login_required(function_based_view) is False
    assert is_login_required(decorated_function_based_view) is True


def test_all_routes_are_authenticated():
    allowed_public_routes = {
        "",
        "favicon.ico",
        "healthcheck/",
        "patients/api/",
        "patients/api/docs",
        "patients/api/openapi.json",
        "patients/invite/<str:token>/accept",
        "private-media/^(?P<path>.*)$",
    }
    found_public_routes = set()

    urls = get_all_urls(get_resolver().url_patterns)
    for url in urls:
        # ignoring admin and allauth routes for now; they don't use the same decorators as the rest of the app
        # Ignore all the anymail routes. These are used for the webhooks
        if url.pattern.startswith(("admin/", "accounts/", "anymail/")):
            continue

        if not is_login_required(url.view):
            found_public_routes.add(url.pattern)

    assert found_public_routes == allowed_public_routes
