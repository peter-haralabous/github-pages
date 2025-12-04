import factory
from factory.django import DjangoModelFactory

from sandwich.core.factories.form_submission import FormSubmissionFactory
from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models.summary import Summary
from sandwich.core.models.summary import SummaryStatus


class SummaryFactory(DjangoModelFactory[Summary]):
    class Meta:
        model = Summary

    patient = factory.SubFactory(PatientFactory)
    organization = factory.SelfAttribute("patient.organization")
    submission = factory.SubFactory(FormSubmissionFactory, patient=factory.SelfAttribute("..patient"), task=None)
    title = factory.Sequence(lambda n: f"Summary {n}")
    body = ""
    status = SummaryStatus.PENDING
