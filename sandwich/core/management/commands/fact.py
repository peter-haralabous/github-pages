from collections.abc import Iterable

from django.core.management import BaseCommand
from django.core.management import CommandParser

from sandwich.core.factories.errors import FactoryError
from sandwich.core.factories.fact import generate_facts_for_predicate
from sandwich.core.management.lib.logging import LoggingMixin
from sandwich.core.management.lib.subcommand import SubcommandMixin
from sandwich.core.management.types import patient_type
from sandwich.core.models import Patient
from sandwich.core.models.predicate import PredicateName


class Command(SubcommandMixin, LoggingMixin, BaseCommand):  # type: ignore[override]
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
                        "choices": PredicateName,
                    },
                ),
                (("--count",), {"help": "Number of facts to generate; default 5", "type": int, "default": 5}),
            ],
        )

    def generate(self, patient: Patient, predicate_names: Iterable[PredicateName], count: int, **_) -> None:
        if not predicate_names:
            predicate_names = PredicateName
        for predicate_name in predicate_names:
            try:
                facts = generate_facts_for_predicate(patient=patient, predicate_name=predicate_name, count=count)
            except FactoryError:
                self.warning(f"{predicate_name} has no matching entities; skipping.")
            else:
                for fact in facts:
                    self.info(f"{fact=}")
