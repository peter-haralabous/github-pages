import pytest
from django.test import Client
from django.test.utils import override_settings
from django.urls import reverse
from pytest_django.asserts import assertContains


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_404_error_page(client: Client):
    response = client.get(reverse("core:healthcheck") + "/thisdoesntexist")
    assert response.status_code == 404
    assertContains(response, "Error 404", status_code=404)
    assertContains(
        response,
        "Oops! We couldn't find the page you're looking for.",
        status_code=404,
    )
    assertContains(response, "Go Back", status_code=404)
    assertContains(response, "Email Support", status_code=404)
    assertContains(response, "Try Again", status_code=404)
