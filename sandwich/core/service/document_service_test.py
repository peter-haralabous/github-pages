import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models.document import Document
from sandwich.core.models.organization import Organization
from sandwich.users.models import User


@pytest.mark.django_db
def test_assign_default_document_permissions_user_owner(user: User) -> None:
    patient = PatientFactory.create(user=user)
    document = Document.objects.create(patient=patient, file=SimpleUploadedFile(name="empty", content=b""))

    assert user.has_perm("view_document", document)
    assert user.has_perm("change_document", document)
    assert user.has_perm("delete_document", document)

    assert user.has_perm("create_document", patient)


@pytest.mark.django_db
def test_assign_default_document_permissions_provider_permissions(
    provider: User, user: User, organization: Organization
) -> None:
    patient = PatientFactory.create(user=user, organization=organization)
    document = Document.objects.create(patient=patient, file=SimpleUploadedFile(name="empty", content=b""))

    assert provider.has_perm("view_document", document)
    assert provider.has_perm("change_document", document)

    assert provider.has_perm("create_document", patient)
