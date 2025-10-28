import factory
from factory.django import DjangoModelFactory
from slugify import slugify

from sandwich.core.models import Organization


class OrganizationFactory(DjangoModelFactory[Organization]):
    class Meta:
        model = Organization
        skip_postgeneration_save = True

    name = factory.Faker("company")
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
