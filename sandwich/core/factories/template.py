import factory

from sandwich.core.models import Template


class TemplateFactory(factory.django.DjangoModelFactory[Template]):
    class Meta:
        model = Template
        django_get_or_create = ("organization", "slug")

    organization = None
    slug = "template/default"
    description = "The default template"
    content = factory.Faker("paragraph", nb_sentences=3)
