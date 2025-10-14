from django.conf import settings
from django.contrib import admin
from django.urls import URLPattern
from django.urls import URLResolver
from django.urls import include
from django.urls import path

urlpatterns: list[URLResolver | URLPattern] = [
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("sandwich.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    path("accounts/", include("allauth.socialaccount.urls")),
    # Anymail webhooks
    path("anymail/", include("anymail.urls", namespace="anymail")),
    path("patients/", include("sandwich.patients.urls", namespace="patients")),
    path("providers/", include("sandwich.providers.urls", namespace="providers")),
    path("", include("sandwich.core.urls", namespace="core")),
]


if settings.SERVE_DJDT:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
        *urlpatterns,
    ]
