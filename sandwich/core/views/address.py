import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from sandwich.core.service.address_service import extract_address_suggestions
from sandwich.core.service.address_service import get_autocomplete_suggestions
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["GET"])
def address_search(request: AuthenticatedHttpRequest) -> HttpResponse:
    logger.info("Address autocomplete endpoint accessed", extra={"user_id": request.user.id})
    query = request.GET.get("query", "").strip()
    logger.debug("Address autocomplete query received", extra={"query": query})

    # No address to lookup?
    if not query:
        return JsonResponse([], safe=False)

    response = get_autocomplete_suggestions(query)

    suggestions = []
    if response:
        suggestions = extract_address_suggestions(response)

    return JsonResponse(suggestions, safe=False)
