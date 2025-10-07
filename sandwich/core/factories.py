import factory
from factory.django import DjangoModelFactory
from slugify import slugify

from sandwich.core.models import Organization
from sandwich.core.models import Patient
from sandwich.core.models import Template
from sandwich.core.service.organization_service import create_default_roles


class OrganizationFactory(DjangoModelFactory[Organization]):
    class Meta:
        model = Organization

    name = factory.Faker("company")
    slug = factory.LazyAttribute(lambda o: slugify(o.name))

    @factory.post_generation
    def create_roles(self: Organization, create, extracted, **kwargs):
        create_default_roles(self)


class PatientFactory(DjangoModelFactory[Patient]):
    class Meta:
        model = Patient

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    date_of_birth = factory.Faker("date_of_birth")


class TemplateFactory(factory.django.DjangoModelFactory[Template]):
    class Meta:
        model = Template
        django_get_or_create = ("organization", "slug")

    organization = None
    slug = "template/default"
    description = "The default template"
    content = factory.Faker("paragraph", nb_sentences=3)
