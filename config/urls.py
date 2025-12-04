import private_storage.urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import URLPattern
from django.urls import URLResolver
from django.urls import include
from django.urls import path

# URLs should be added to a namespace if at all possible to allow consistent targeting by middleware
# See: ConsentMiddleware, PatientAccessMiddleware
urlpatterns: list[URLResolver | URLPattern] = [
    # namespace=admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    path("users/", include("sandwich.users.urls", namespace="users")),
    # NO NAMESPACE; allauth doesn't support; bad allauth
    path("accounts/", include("allauth.urls")),
    path("accounts/", include("allauth.socialaccount.urls")),
    path("anymail/", include("anymail.urls", namespace="anymail")),
    path("patients/", include("sandwich.patients.urls", namespace="patients")),
    path("providers/", include("sandwich.providers.urls", namespace="providers")),
    path("", include("sandwich.core.urls", namespace="core")),
    # NO NAMESPACE; private_storage doesn't support; bad private_storage
    path("private-media/", include(private_storage.urls)),
]

# in production files live in S3 and this route doesn't exist
if settings.SERVE_MEDIA:
    urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))

if settings.SERVE_DJDT:
    import debug_toolbar

    # namespace=djdt
    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
        *urlpatterns,
    ]
