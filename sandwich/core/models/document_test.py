from unittest.mock import patch

import pytest

from sandwich.core.models.document import Document
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.patient import Patient


@pytest.mark.django_db
def test_document_create_assigns_permissions(patient: Patient, encounter: Encounter) -> None:
    # test for assign_default_document_permissions can be found in
    # sandwich/core/service/document_service_test.py
    with patch("sandwich.core.service.document_service.assign_default_document_permissions") as mock_create:
        created = Document.objects.create(patient=patient, encounter=encounter)
        mock_create.assert_called_once_with(created)
