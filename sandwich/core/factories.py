import factory
from factory.django import DjangoModelFactory

from sandwich.core.models import Organization
from sandwich.core.models import Template
from sandwich.core.service.organization_service import create_default_roles


class OrganizationFactory(DjangoModelFactory):
    class Meta:
        model = Organization

    name = factory.Faker("company")

    @factory.post_generation
    def create_roles(self: Organization, create, extracted, **kwargs):
        create_default_roles(self)


class TemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Template
        django_get_or_create = ("organization", "slug")

    organization = None
    slug = "template/default"
    description = "The default template"
    content = factory.Faker("paragraph", nb_sentences=3)
