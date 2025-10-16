import factory
from factory.django import DjangoModelFactory
from slugify import slugify

from sandwich.core.models import Consent
from sandwich.core.models import Organization
from sandwich.core.models import Patient
from sandwich.core.models import Template
from sandwich.core.models.consent import ConsentPolicy
from sandwich.core.service.organization_service import create_default_roles_and_perms


class ConsentFactory(DjangoModelFactory[Consent]):
    user = factory.SubFactory("sandwich.users.factories.UserFactory")
    policy = ConsentPolicy.THRIVE_PRIVACY_POLICY
    decision = True

    class Meta:
        model = Consent
        skip_postgeneration_save = True


class OrganizationFactory(DjangoModelFactory[Organization]):
    class Meta:
        model = Organization
        skip_postgeneration_save = True

    name = factory.Faker("company")
    slug = factory.LazyAttribute(lambda o: slugify(o.name))

    @factory.post_generation
    def create_roles(self: Organization, create, extracted, **kwargs):
        create_default_roles_and_perms(self)


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
