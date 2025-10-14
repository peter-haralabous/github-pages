import private_storage.urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.templatetags.static import static as resolve_static
from django.urls import URLPattern
from django.urls import URLResolver
from django.urls import include
from django.urls import path
from django.views import defaults as default_views
from django.views.generic import RedirectView
from django.views.generic import TemplateView

urlpatterns: list[URLResolver | URLPattern] = [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("sandwich.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    path("accounts/", include("allauth.socialaccount.urls")),
    # Anymail webhooks
    path("anymail/", include("anymail.urls")),
    # Your stuff: custom urls includes go here
    path("", include("sandwich.core.urls", namespace="core")),
    path("patients/", include("sandwich.patients.urls", namespace="patients")),
    path("providers/", include("sandwich.providers.urls", namespace="providers")),
    # Media files
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    path("private-media/", include(private_storage.urls)),
    path("favicon.ico", RedirectView.as_view(url=resolve_static("images/favicons/favicon.ico"))),
]


if settings.SERVE_ERROR_VIEWS:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]

if settings.SERVE_DJDT:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
        *urlpatterns,
    ]
