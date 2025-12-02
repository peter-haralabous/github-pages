import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse

from sandwich.core.service.medication_service import get_mediction_results

logger = logging.getLogger(__name__)


@login_required
def medication_search(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("query")
    logger.info("Medication search query received", extra={"query": query})
    return JsonResponse(get_mediction_results(query), safe=False)
