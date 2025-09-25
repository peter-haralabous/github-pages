from django.http import HttpRequest

from sandwich.users.models import User


# https://github.com/typeddjango/django-stubs#how-can-i-create-a-httprequest-thats-guaranteed-to-have-an-authenticated-user
class AuthenticatedHttpRequest(HttpRequest):
    """If your view function is decorated with @login_required, use this type for the request parameter."""

    user: User


def validate_sort(sort: str | None, valid_sorts: list[str]) -> str | None:
    """validate a ?sort=foo query string"""
    if sort is None:
        return None
    field = sort[1:] if sort.startswith("-") else sort
    if field not in valid_sorts:
        return None
    return sort
