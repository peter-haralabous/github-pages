import uuid
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.urls import reverse

from sandwich.core.factories import OrganizationFactory
from sandwich.core.models.role import RoleName
from sandwich.core.service.organization_service import assign_organization_role
from sandwich.providers.views.home import home
from sandwich.providers.views.home import organization_home
from sandwich.users.factories import UserFactory

# mypy: disable-error-code="arg-type, assignment"


@pytest.mark.django_db
@patch("sandwich.providers.views.home.render")
def test_home_renders_template_with_multiple_organizations(mock_render, rf: RequestFactory):
    """Test that home view renders template when user has multiple organizations."""
    user = UserFactory()
    request = rf.get("/")
    request.user = user

    organizations = OrganizationFactory.create_batch(2)
    for organization in organizations:
        assign_organization_role(organization, RoleName.OWNER, user)

    mock_response = Mock()
    mock_render.return_value = mock_response

    response = home(request)

    mock_render.assert_called_once()
    args, _ = mock_render.call_args
    assert args[0] == request
    assert args[1] == "provider/home.html"
    assert "organizations" in args[2]
    assert list(args[2]["organizations"]) == organizations

    assert response == mock_response


@pytest.mark.django_db
@patch("sandwich.providers.views.home.render")
def test_home_renders_template_with_no_organizations(mock_render, rf: RequestFactory):
    """Test that home view renders template when user has no organizations."""
    user = UserFactory()
    request = rf.get("/")
    request.user = user

    mock_response = Mock()
    mock_render.return_value = mock_response

    response = home(request)

    mock_render.assert_called_once()
    args, _ = mock_render.call_args
    assert args[0] == request
    assert args[1] == "provider/home.html"
    assert "organizations" in args[2]
    assert list(args[2]["organizations"]) == []

    assert response == mock_response


@pytest.mark.django_db
def test_home_redirects_to_organization_when_single_org(rf: RequestFactory):
    """Test that home view redirects to organization page when user has exactly one organization."""
    user = UserFactory()
    request = rf.get("/")
    request.user = user

    organization = OrganizationFactory.create()
    assign_organization_role(organization, RoleName.OWNER, user)

    response = home(request)

    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse("providers:organization", kwargs={"organization_id": organization.id})


@pytest.mark.django_db
def test_organization_home_redirects_to_encounter_list(rf: RequestFactory):
    """Test that organization_home redirects to encounter list."""
    user = UserFactory()
    request = rf.get("/")
    request.user = user
    organization_id = uuid.uuid4()

    response = organization_home(request, organization_id)

    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse("providers:encounter_list", kwargs={"organization_id": organization_id})
