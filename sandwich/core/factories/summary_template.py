import factory
from factory.django import DjangoModelFactory

from sandwich.core.factories.form import FormFactory
from sandwich.core.factories.organization import OrganizationFactory
from sandwich.core.models.summary_template import SummaryTemplate


class SummaryTemplateFactory(DjangoModelFactory[SummaryTemplate]):
    class Meta:
        model = SummaryTemplate

    organization = factory.SubFactory(OrganizationFactory)
    form = factory.SubFactory(FormFactory, organization=factory.SelfAttribute("..organization"))
    name = factory.Sequence(lambda n: f"Summary Template {n}")
    description = ""
    text = "# Summary\n\n{% ai 'Generate summary' %}"
