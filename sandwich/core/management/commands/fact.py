from collections.abc import Iterable

from django.core.management import BaseCommand
from django.core.management import CommandParser

from sandwich.core.factories.fact import generate_facts_for_predicate
from sandwich.core.factories.fact import predicate_entity_map
from sandwich.core.management.lib.subcommand import SubcommandMixin
from sandwich.core.management.types import patient_type
from sandwich.core.models import Patient
from sandwich.core.models.predicate import PredicateName

supported_predicate_names = predicate_entity_map.keys()


class Command(SubcommandMixin, BaseCommand):  # type: ignore[override]
    noun = "Fact"

    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)
        self.add_subcommand(
            "generate",
            self.generate,
            arguments=[
                (("patient",), {"type": patient_type, "help": "Patient to generate facts for"}),
                (
                    ("predicate_names",),
                    {
                        "nargs": "*",
                        "help": "Predicates to generate facts for; defaults to all valid choices",
                        "type": PredicateName,
                        "choices": supported_predicate_names,
                    },
                ),
                (("--count",), {"help": "Number of facts to generate; default 5", "type": int, "default": 5}),
            ],
        )

    def generate(self, patient: Patient, predicate_names: Iterable[PredicateName], count: int, **_) -> None:
        if not predicate_names:
            predicate_names = supported_predicate_names
        for predicate_name in predicate_names:
            generate_facts_for_predicate(patient=patient, predicate_name=predicate_name, count=count)
