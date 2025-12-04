from urllib.parse import urlencode

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import SafeString

from sandwich.core.factories.errors import FactoryError
from sandwich.core.factories.fact import generate_facts_for_predicate
from sandwich.core.models import Fact
from sandwich.core.models import Patient
from sandwich.core.models.predicate import PredicateName
from sandwich.core.util.http import AuthenticatedHttpRequest


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "organization_id", "user_id")
    actions = ["generate_facts"]

    @admin.action(description="Generate facts for selected patients")
    def generate_facts(self, request, queryset):
        selected = queryset.values_list("pk", flat=True)
        url = reverse("admin:generate_patient_facts")
        data = {**request.GET, "ids": ",".join(str(pk) for pk in selected)}
        return HttpResponseRedirect(f"{url}?{urlencode(data)}")

    def get_urls(self):
        return [
            path(
                "generate_facts/",
                self.admin_site.admin_view(generate_patient_facts),
                name="generate_patient_facts",
            ),
            *super().get_urls(),
        ]


def predicate_field_name(predicate: PredicateName) -> str:
    """Generate a form field name from a predicate name."""
    return f"predicate_{predicate.value.lower().replace(' ', '_')}"


def facts_result_message(facts: list[Fact]) -> SafeString:
    """Format a html message to send back to the admin on fact creation"""
    patient = facts[0].subject
    return format_html(
        "Generated {count} facts for <a href='{url}'>{patient}</a>",
        count=len(facts),
        url=reverse("admin:core_fact_changelist", query={"subject_id": patient.id}),
        patient_id=patient.id,
        patient=patient,
    )


class GenerateFactsForm(forms.Form):
    """Form to provide options for PatientAdmin.generate_facts"""

    ids = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(Submit("save", "Generate"))

        for predicate_name in PredicateName:
            self.fields[predicate_field_name(predicate_name)] = forms.IntegerField(
                initial=5,
                min_value=0,
                required=False,
                label=predicate_name.value,
                help_text=f"Number of facts to generate for {predicate_name.value}",
            )


def missing_object_message(predicate_name):
    """Generate an error message for missing entities for a predicate."""
    return format_html(
        "Cannot generate facts for predicate <strong>{}</strong>: no matching object entities found.",
        predicate_name.value,
    )


def generate_patient_facts(request: AuthenticatedHttpRequest) -> HttpResponse:
    """View to generate facts for selected patients via PatientAdmin.generate_facts"""
    form = GenerateFactsForm(request.POST or request.GET or {})
    if request.method == "POST" and form.is_valid():
        for patient_id in form.cleaned_data["ids"].split(","):
            patient = Patient.objects.get(pk=patient_id)
            facts = []
            for predicate_name in PredicateName:
                count = form.cleaned_data[predicate_field_name(predicate_name)]
                if count:
                    try:
                        facts += generate_facts_for_predicate(patient, predicate_name, count)
                    except FactoryError:
                        messages.error(request, missing_object_message(predicate_name))
            if facts:
                messages.success(request, facts_result_message(facts))
        return HttpResponseRedirect(reverse("admin:core_patient_changelist"))
    return TemplateResponse(
        request,
        "admin/core/patient/generate_facts.html",
        {
            "form": form,
        },
    )
