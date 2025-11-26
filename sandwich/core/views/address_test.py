from http import HTTPStatus
from unittest import mock
from unittest.mock import MagicMock

import pytest
from django.test import Client
from django.urls import reverse

from sandwich.users.models import User


@mock.patch("sandwich.core.views.address.get_autocomplete_suggestions")
@pytest.mark.django_db
def test_address_search_no_query_returns_no_data(mock_get_suggestions: MagicMock, client: Client, user: User):
    client.force_login(user)
    url = reverse("core:address_search")
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert response.context is None
    # No query provided, so no suggestions should be fetched
    mock_get_suggestions.assert_not_called()


@mock.patch("sandwich.core.views.address.get_autocomplete_suggestions")
@pytest.mark.django_db
def test_address_search_with_query_returns_suggestions(mock_get_suggestions: MagicMock, client: Client, user: User):
    client.force_login(user)
    url = reverse("core:address_search")
    mock_get_suggestions.return_value = {
        "suggestions": [
            {"placePrediction": {"text": {"text": "123 Main St, Vancouver, BC"}}},
            {"placePrediction": {"text": {"text": "456 Another Rd, Vancouver, BC"}}},
        ]
    }

    response = client.get(url, {"query": "123 Main"})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        "123 Main St, Vancouver, BC",
        "456 Another Rd, Vancouver, BC",
    ]
    mock_get_suggestions.assert_called_once_with("123 Main")
