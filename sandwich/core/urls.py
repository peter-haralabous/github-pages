from django.urls import path

from sandwich.core.views import healthcheck
from sandwich.core.views.account import account_delete
from sandwich.core.views.legal import legal_view

app_name = "core"
urlpatterns = [
    path("healthcheck/", healthcheck.healthcheck, name="healthcheck"),
    path("delete-account/", account_delete, name="account_delete"),
    path("legal/", legal_view, name="legal"),
]
