import factory
from factory.django import DjangoModelFactory

from sandwich.core.factories.organization import OrganizationFactory
from sandwich.core.models import Form


class FormFactory(DjangoModelFactory[Form]):
    class Meta:
        model = Form

    name = factory.Sequence(lambda n: f"Form {n}")
    schema = factory.LazyFunction(lambda: {"elements": []})
    organization = factory.SubFactory(OrganizationFactory)
