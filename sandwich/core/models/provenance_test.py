import datetime

import django.db
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from sandwich.core.models import Document
from sandwich.core.models import Patient
from sandwich.core.models import Provenance
from sandwich.core.models.provenance import SourceTypes
from sandwich.users.models import User


@pytest.mark.django_db
def test_provenance_url_property():
    patient = Patient.objects.create(date_of_birth=datetime.date(2000, 1, 1))
    test_file = SimpleUploadedFile("doc.pdf", b"dummy content")
    doc = Document.objects.create(patient=patient, file=test_file)

    # Provenance with page
    prov = Provenance(document=doc, page=2)
    assert prov.url is not None
    assert prov.url.endswith("#page=2")
    assert prov.url.endswith(".pdf#page=2")

    # Provenance without page
    prov2 = Provenance(document=doc, page=None)
    assert prov2.url is not None
    assert prov2.url.endswith(".pdf")

    # Provenance with no document
    prov3 = Provenance(document=None)
    assert prov3.url is None


@pytest.mark.django_db(transaction=True)
def test_provenance_user_constraint_text():
    patient = Patient.objects.create(date_of_birth=datetime.date(2000, 1, 1))
    test_file = SimpleUploadedFile("doc.pdf", b"dummy content")
    doc = Document.objects.create(patient=patient, file=test_file)
    # User not provided
    with pytest.raises(django.db.utils.IntegrityError):
        Provenance.objects.create(document=doc, source_type=SourceTypes.TEXT, user=None)

    # User is provided
    user = User.objects.create()
    prov = Provenance.objects.create(document=doc, source_type=SourceTypes.TEXT, user=user)
    assert prov.user == user


@pytest.mark.django_db
def test_provenance_user_constraint_not_text():
    patient = Patient.objects.create(date_of_birth=datetime.date(2000, 1, 1))
    test_file = SimpleUploadedFile("doc.pdf", b"dummy content")
    doc = Document.objects.create(patient=patient, file=test_file)
    prov = Provenance.objects.create(document=doc, source_type=SourceTypes.DOCUMENT, user=None)
    assert prov.user is None
