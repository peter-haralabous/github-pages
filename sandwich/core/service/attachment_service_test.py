import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models import Attachment
from sandwich.core.models.organization import Organization
from sandwich.fixtures.default import EncounterFactory
from sandwich.users.models import User


@pytest.mark.django_db
def test_assign_default_attachment_permissions(user: User, provider: User, organization: Organization) -> None:
    patient = PatientFactory.create(user=user, organization=organization)
    EncounterFactory.create(organization=organization, patient=patient)

    attachment = Attachment.objects.create(
        uploaded_by=user,
        file=SimpleUploadedFile(name="test", content=b""),
        original_filename="test",
        content_type="jpg",
    )

    assert user.has_perm("view_attachment", attachment)
    assert user.has_perm("change_attachment", attachment)
    assert user.has_perm("delete_attachment", attachment)

    assert provider.has_perm("view_attachment", attachment)
