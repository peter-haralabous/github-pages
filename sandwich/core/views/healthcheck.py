from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone


def healthcheck(request):
    """
    Healthcheck endpoint.
    """
    return JsonResponse({"datetime": timezone.now(), "version": settings.APP_VERSION})
