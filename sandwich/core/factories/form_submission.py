import factory
from factory.django import DjangoModelFactory

from sandwich.core.factories.task import TaskFactory
from sandwich.core.models.form_submission import FormSubmission
from sandwich.core.models.form_submission import FormSubmissionStatus


class FormSubmissionFactory(DjangoModelFactory[FormSubmission]):
    class Meta:
        model = FormSubmission

    task = factory.SubFactory(TaskFactory)
    patient = factory.SelfAttribute("task.patient")
    status = FormSubmissionStatus.DRAFT
    data = factory.LazyFunction(dict)
    metadata = factory.LazyFunction(dict)
