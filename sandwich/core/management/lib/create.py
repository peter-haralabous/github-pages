from abc import ABC
from argparse import ArgumentParser
from collections.abc import Sequence
from typing import Any
from typing import Protocol
from typing import cast

import factory
from django.core.management.base import CommandParser
from django.db.models import Model
from factory import Factory

from sandwich.core.management.lib.factory import FactoryMixinProtocol
from sandwich.core.management.lib.factory import FactoryWrapper
from sandwich.core.management.lib.model import ModelReportMixinProtocol
from sandwich.core.management.lib.report import ReportMixinProtocol
from sandwich.core.management.lib.subcommand import Args
from sandwich.core.management.lib.subcommand import SubcommandMixinProtocol


class CreateSubcommandMixinProtocol[M: Model](
    Protocol,
):
    """Mixin protocol for CreateSubcommandMixin subclasses"""

    factory: type[factory.Factory]

    def add_create_arguments(self) -> ArgumentParser: ...
    def create_arguments(self) -> Sequence[Args]: ...
    def create(self, **kwargs: Any) -> Sequence[M]: ...
    def create_output(self, objects: Sequence[M], **kwargs: Any) -> None: ...


class SelfProtocol[M: Model](
    CreateSubcommandMixinProtocol,
    FactoryMixinProtocol,
    ModelReportMixinProtocol,
    ReportMixinProtocol,
    SubcommandMixinProtocol,
    Protocol,
):
    """Private protocol for CreateSubcommandMixin"""


class CreateSubcommandMixin[M: Model](ABC):
    """A mixin to support creating model instances as a subcommand of a django management command

    ! Intended for use with FactoryMixin, ModelReportMixin, ReportMixin, SubcommandMixin and BaseCommand
    """

    factory: type[Factory]

    def add_arguments(self: SelfProtocol[M], parser: CommandParser) -> None:
        super().add_arguments(parser)  # type: ignore[misc]
        self.add_create_arguments()

    def add_create_arguments(self: SelfProtocol[M]) -> ArgumentParser:
        subcommand = self.add_subcommand(
            "create",
            self.create,
            self.create_arguments(),
            aliases=["c", "generate", "g"],
        )
        self.add_factory_arguments(subcommand)
        self.add_report_arguments(subcommand)
        return subcommand

    def create_arguments(self: SelfProtocol[M]) -> Sequence[Args]:
        """The arguments used to initialize the argument parser for the create subcommand"""
        return []

    def create(
        self,
        **options: Any,
    ) -> Sequence[M]:
        """Create objects from the factory and output the results."""
        objects = cast("Sequence[M]", FactoryWrapper(self.factory).handle_factory(**options))
        self.create_output(objects)  # type: ignore[misc]
        return objects

    def create_output(self: SelfProtocol[M], objects: Sequence[M], **kwargs: Any) -> None:
        """Output the list of objects."""
        self.model_report(objects, **kwargs)
