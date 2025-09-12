# adapted from https://www.loopwerk.io/articles/2025/django-local-times/

from zoneinfo import ZoneInfo

from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.COOKIES.get("timezone")
        if tzname:
            try:
                # Activate the timezone for this request
                timezone.activate(ZoneInfo(tzname))
            except Exception:  # noqa: BLE001
                # Fallback to the project's default timezone if the name is invalid
                timezone.deactivate()
        else:
            # No cookie, so use the project's default timezone
            timezone.deactivate()

        return self.get_response(request)
