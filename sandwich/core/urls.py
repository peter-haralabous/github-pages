from django.conf import settings
from django.templatetags.static import static as resolve_static
from django.urls import path
from django.views import defaults as default_views
from django.views.csrf import csrf_failure
from django.views.generic import RedirectView

from sandwich.core.eventstream import events_view
from sandwich.core.views.account import account_delete
from sandwich.core.views.address import address_search
from sandwich.core.views.attachment import attachment_by_id
from sandwich.core.views.attachment import attachment_delete
from sandwich.core.views.attachment import attachment_upload
from sandwich.core.views.healthcheck import healthcheck
from sandwich.core.views.home import home
from sandwich.core.views.legal import legal_view
from sandwich.core.views.medication import medication_search
from sandwich.core.views.notifications import account_notifications
from sandwich.core.views.policy import policy_detail
from sandwich.core.views.switcher import switcher

app_name = "core"
urlpatterns = [
    path("", home, name="home"),
    path("switcher/", switcher, name="switcher"),
    path("healthcheck/", healthcheck, name="healthcheck"),
    path("delete-account/", account_delete, name="account_delete"),
    path("notifications", account_notifications, name="account_notifications"),
    path("legal/", legal_view, name="legal"),
    path("favicon.ico", RedirectView.as_view(url=resolve_static("images/favicons/favicon.ico"))),
    path("policy/<slug:slug>/", policy_detail, name="policy_detail"),
    path("events/", events_view, name="events"),
    path("address-search/", address_search, name="address_search"),
    path("api/attachments/upload", attachment_upload, name="attachment_upload"),
    path("api/attachments/<uuid:attachment_id>/delete", attachment_delete, name="attachment_delete"),
    path("api/attachments/<uuid:attachment_id>/", attachment_by_id, name="attachment_by_id"),
    path("api/medication-search/", medication_search, name="medication_search"),
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
            "403_csrf/",
            csrf_failure,
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
