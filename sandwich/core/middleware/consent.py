import logging
import re
from collections.abc import Callable
from functools import cached_property
from typing import TypeGuard

from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import ResolverMatch
from django.urls import reverse

from sandwich.core.models.consent import Consent
from sandwich.core.models.consent import ConsentPolicy
from sandwich.core.types import RePattern
from sandwich.core.types import UrlNamespace
from sandwich.core.types import ViewName
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.core.util.http import cached_resolve
from sandwich.users.models import User


def _has_consented_to_policies(user: User, policies: set[ConsentPolicy]) -> bool:
    consented_policies = {c.policy for c in Consent.objects.for_user(user) if c.decision is True}
    return policies.issubset(consented_policies)


def _handle_missing_consent(request: HttpRequest) -> HttpResponse:
    url = reverse("patients:consent")  # Providers too for now
    return HttpResponseRedirect(f"{url}?next={request.path}")


class ConsentMiddleware:
    exempt_namespaces: set[UrlNamespace] = {
        "admin",
        "anymail",
        "debug_toolbar",
        "http_response",
        "patients:api-1.0.0",
        "static",
    }

    exempt_view_names: set[ViewName] = {
        "core:healthcheck",
        "core:home",
        "patients:consent",
        "serve_private_file",
    }

    exempt_route_patterns: set[RePattern] = set(
        "^accounts/"  # allauth urls don't support namespaces
    )

    required_policies: set[ConsentPolicy] = {
        ConsentPolicy.THRIVE_PRIVACY_POLICY,
        ConsentPolicy.THRIVE_TERMS_OF_USE,
    }

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        match = cached_resolve(request)

        if self.should_process(request, match):
            return self.process(request)
        return self.get_response(request)

    @cached_property
    def exempt_route_pattern(self) -> re.Pattern[str]:
        return re.compile("|".join([re.escape(p) for p in self.exempt_route_patterns]))

    def should_process(self, request: HttpRequest, match: ResolverMatch) -> TypeGuard[AuthenticatedHttpRequest]:
        logging.debug(f"should_process: {match.namespace=} {match.view_name=} {match.route=}")  # noqa:G004
        return (
            request.user.is_authenticated
            and match.namespace not in self.exempt_namespaces
            and match.view_name not in self.exempt_view_names
            and not self.exempt_route_pattern.match(match.route)
        )

    def process(self, request: AuthenticatedHttpRequest) -> HttpResponse:
        if _has_consented_to_policies(request.user, self.required_policies):
            return self.get_response(request)
        return _handle_missing_consent(request)
