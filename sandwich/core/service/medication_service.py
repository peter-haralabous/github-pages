import logging
from json import JSONDecodeError

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

DRUGBANK_BASE_URL = "https://api.drugbank.com"


def _extract_medication_results(results: list[dict]) -> list[dict]:
    """
    Parses only the medication details we care about from the larger drugbank
    response.
    """
    medications = []
    for result in results:
        drugbank_id = result.get("drugbank_pcid")
        name = result.get("name")
        # Drugbank results should always have a `name` and `id`. If not, skip
        # this result and log the malformed data.
        if drugbank_id is None or name is None:
            logger.info("Medication result malformed", extra={"result": result})
            continue

        medications.append(
            {
                "drugbank_id": drugbank_id,
                "name": name,
                "display_name": result.get("display_name"),
            }
        )

    return medications


def get_mediction_results(query: str | None) -> list[dict]:
    """
    Use the drugbank API to lookup a medication.
    """

    if not query:
        return []

    url = f"{DRUGBANK_BASE_URL}/v1/product_concepts"

    try:
        res = requests.get(url, params={"q": query}, headers={"Authorization": settings.DRUGBANK_API_KEY}, timeout=10)

        res.raise_for_status()
        results = res.json()

    except requests.HTTPError as e:
        logger.exception(
            "HTTP error when connecting to DrugBank API", extra={"status_code": e.response.status_code, "query": query}
        )
        return []

    except JSONDecodeError:
        logger.exception("Error parsing DrugBank API response")
        return []

    except requests.RequestException:
        logger.exception("Error connecting to DrugBank API")
        return []

    return _extract_medication_results(results)
