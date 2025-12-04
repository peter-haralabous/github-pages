from django.urls import path

from .views import user_detail_view
from .views import user_redirect_view

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("<int:pk>/", view=user_detail_view, name="detail"),
    # Note: Before adding new routes here, see the README.md file in this directory.
]
