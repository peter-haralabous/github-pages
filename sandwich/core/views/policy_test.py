import pytest
from django.test import Client
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_policy_view_renders_test_policy(client: Client):
    url = reverse("core:policy_detail", args=["privacy-notice"])
    response = client.get(url)
    assert response.status_code == 200
    assert "<h1" in response.content.decode()
    assert "<div" in response.content.decode()


def test_policy_view_404_for_invalid_slug(client: Client):
    url = reverse("core:policy_detail", args=["not-a-real-policy"])
    response = client.get(url)
    assert response.status_code == 404
