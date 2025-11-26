import logging
from typing import Any

from django.conf import settings
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class LocationBoundary:
    """Location boundary configurations for Google Places API autocomplete."""

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


def extract_address_suggestions(response_data: dict) -> list[str]:
    """Extract address suggestions from Google Places API response data.

    Returns a list of address strings.
    e.g. ["123 Main St, Vancouver, BC", "456 Another Rd, Vancouver, BC", ...]
    """
    suggestions = []
    for autocomplete_suggestion in response_data.get("suggestions", []):
        place_prediction = autocomplete_suggestion.get("placePrediction")
        address = place_prediction.get("text").get("text")
        suggestions.append(address)
    return suggestions


def get_autocomplete_suggestions(query: str) -> dict[str, Any]:
    """Call Google Places API for address autocomplete.

    Returns the API response as a dictionary.

    List of supported Google APIs:
    https://github.com/googleapis/google-api-python-client/blob/main/docs/dyn/index.md
    https://googleapis.github.io/google-api-python-client/docs/dyn/places_v1.places.html#autocomplete
    """
    logger.debug("Calling Google Places API for autocomplete suggestions", extra={"query": query})
    with build("places", "v1", developerKey=settings.GOOGLE_API_KEY) as service:
        try:
            # TODO: add "sessionToken" param to improve billing, but how to generate it? can't find docs for this
            return (
                service.places()
                .autocomplete(
                    body={
                        "input": query,
                        "locationRestriction": LocationBoundary.CANADA,
                    }
                )
                .execute()
            )
        except HttpError as e:
            logger.info(f"Error response status code : {e.status_code}, reason : {e.error_details}")  # noqa: G004
            return {}
