from unittest.mock import patch

import pytest

from sandwich.core.models.invitation import Invitation
from sandwich.core.models.invitation import InvitationStatus
from sandwich.core.models.patient import Patient


@pytest.mark.django_db
def test_invitation_creation_assigns_permissions(patient: Patient) -> None:
    # test for assign_default_invitation_perms can be found in
    # sandwich/core/service/document_service_test.py
    with patch("sandwich.core.service.invitation_service.assign_default_invitation_perms") as mock_create:
        created = Invitation.objects.create(status=InvitationStatus.PENDING, token="", patient=patient)
        mock_create.assert_called_once_with(created)
