"""Helpers for managing list view filter state."""

from __future__ import annotations

from typing import Any

from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import QueryDict

from sandwich.core.service.list_preference_service import encode_filters_to_url_params


def _serialize_filter_query_params(query_params: QueryDict) -> dict[str, str]:
    """Convert filter_* query params into a comparable dictionary."""
    serialized: dict[str, str] = {}
    for key, values in query_params.lists():
        if not key.startswith("filter_"):
            continue
        serialized[key] = ",".join(str(value) for value in values if value is not None)
    return serialized


def maybe_redirect_with_saved_filters(  # noqa: PLR0911
    request: HttpRequest,
    saved_filters: dict[str, Any] | None,
) -> HttpResponse | None:
    """Redirect to a canonical URL that reflects saved filters when needed."""
    if request.method != "GET":
        return None

    # Don't apply saved filters if user is in custom filter mode
    filter_mode = request.GET.get("filter_mode")
    if filter_mode == "custom":
        return None

    saved_params = encode_filters_to_url_params(saved_filters or {})
    if not saved_params:
        return None

    current_filters = _serialize_filter_query_params(request.GET)
    if current_filters:
        return None

    canonical_params = QueryDict(mutable=True)
    for key, values in request.GET.lists():
        canonical_params.setlist(key, values)

    for key, value in saved_params.items():
        canonical_params[key] = value

    canonical_query = canonical_params.urlencode()
    target_url = request.path if not canonical_query else f"{request.path}?{canonical_query}"

    if target_url == request.get_full_path():
        return None

    if request.headers.get("HX-Request"):
        response = HttpResponse(status=200)
        response["HX-Redirect"] = target_url
        return response

    return HttpResponseRedirect(target_url)
