from unittest.mock import patch

import pytest

from sandwich.core.models import Organization


@pytest.mark.django_db
def test_organization_create_assigns_permissions() -> None:
    # test for create_default_roles_and_perms can be found in
    # sandwich/core/service/organization_service_test.py
    with patch("sandwich.core.service.organization_service.create_default_roles_and_perms") as mock_create:
        created = Organization.objects.create(name="test org", slug="is_this_unique")
        mock_create.assert_called_once_with(created)
