from django.urls import path

from .views import account_delete

app_name = "accounts"
urlpatterns = [
    path("delete", account_delete, name="delete"),
]
