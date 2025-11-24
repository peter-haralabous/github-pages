import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


class LocationBias:
    """Location bias configurations for Google Places API autocomplete."""

    CANADA = {
        "rectangle": {
            "low": {
                "latitude": 41.6765,  # Southernmost point (near Lake Erie)
                "longitude": -141.0027,  # Westernmost point (Yukon border)
            },
            "high": {
                "latitude": 83.1139,  # Northernmost point (near North Pole)
                "longitude": -52.6194,  # Easternmost point (Newfoundland)
            },
        }
    }


@login_required
@require_http_methods(["GET"])
def address_search(request: AuthenticatedHttpRequest) -> HttpResponse:
    logger.info("Address autocomplete endpoint accessed", extra={"user_id": request.user.id})
    query = request.GET.get("query", "").strip()
    logger.debug("Address autocomplete query received", extra={"query": query})

    # No address to lookup?
    if not query:
        return JsonResponse([], safe=False)

    # List of supported Google APIs:
    # https://github.com/googleapis/google-api-python-client/blob/main/docs/dyn/index.md
    # https://googleapis.github.io/google-api-python-client/docs/dyn/places_v1.places.html#autocomplete
    suggestions = []
    with build("places", "v1", developerKey=settings.GOOGLE_API_KEY) as service:
        try:
            # TODO: add "sessionToken" param to improve billing, but how to generate it? can't find docs for this
            response = (
                service.places()
                .autocomplete(
                    body={
                        "input": query,
                        "locationBias": LocationBias.CANADA,
                    }
                )
                .execute()
            )
        except HttpError as e:
            logger.info(f"Error response status code : {e.status_code}, reason : {e.error_details}")  # noqa: G004

        if response:
            # Build a list of address strings
            # (e.g. ["123 Main St, Vancouver, BC", "456 Another Rd, Vancouver, BC", ...])
            for autocomplete_suggestion in response.get("suggestions", []):
                place_prediction = autocomplete_suggestion.get("placePrediction")
                address = place_prediction.get("text").get("text")
                suggestions.append(address)

    return JsonResponse(suggestions, safe=False)
