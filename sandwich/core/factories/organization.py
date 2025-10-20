import factory
from factory.django import DjangoModelFactory
from slugify import slugify

from sandwich.core.models import Organization
from sandwich.core.service.organization_service import create_default_roles_and_perms


class OrganizationFactory(DjangoModelFactory[Organization]):
    class Meta:
        model = Organization
        skip_postgeneration_save = True

    name = factory.Faker("company")
    slug = factory.LazyAttribute(lambda o: slugify(o.name))

    @factory.post_generation
    def create_roles(self: Organization, create, extracted, **kwargs):
        create_default_roles_and_perms(self)
