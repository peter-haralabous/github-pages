from django.contrib.auth.models import AnonymousUser
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpRequest
from django.urls import ResolverMatch
from django.urls import resolve

from sandwich.users.models import User


class UserHttpRequest(WSGIRequest):
    """If your view function is NOT decorated with @login_required, use this type for the request parameter."""

    user: User | AnonymousUser


# https://github.com/typeddjango/django-stubs#how-can-i-create-a-httprequest-thats-guaranteed-to-have-an-authenticated-user
class AuthenticatedHttpRequest(HttpRequest):
    """If your view function is decorated with @login_required, use this type for the request parameter."""

    user: User


def cached_resolve(request: HttpRequest) -> ResolverMatch:
    if not hasattr(request, "_resolved"):
        request._resolved = resolve(request.path)  # type: ignore[attr-defined]  # noqa: SLF001
    return request._resolved  # type: ignore[attr-defined] # noqa: SLF001


def validate_sort(sort: str | None, valid_sorts: list[str]) -> str | None:
    """validate a ?sort=foo query string"""
    if sort is None:
        return None
    field = sort[1:] if sort.startswith("-") else sort
    if field not in valid_sorts:
        return None
    return sort
