from django.conf import settings
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.utils import timezone


def healthcheck(request: HttpRequest):
    """
    Healthcheck endpoint.
    """
    if request.user.is_superuser:
        if error_code := request.GET.get("error_code"):
            return HttpResponse(status_code=int(error_code), content="Simulated error")
    return JsonResponse({"datetime": timezone.now(), "version": settings.APP_VERSION})
