from uuid import uuid4

import factory
from factory.django import DjangoModelFactory

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models import Invitation
from sandwich.core.models.invitation import InvitationStatus


class InvitationFactory(DjangoModelFactory[Invitation]):
    class Meta:
        model = Invitation

    status = InvitationStatus.PENDING
    token = factory.LazyAttribute(lambda _: uuid4())
    patient = factory.SubFactory(PatientFactory)
