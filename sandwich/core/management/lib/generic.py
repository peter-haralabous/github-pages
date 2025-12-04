# mypy: disable-error-code="name-defined"
from abc import ABC
from typing import Protocol

import factory
from django.core.management.base import BaseCommand
from django.db.models import Model

from sandwich.core.management.lib.create import CreateSubcommandMixin
from sandwich.core.management.lib.create import CreateSubcommandMixinProtocol
from sandwich.core.management.lib.delete import DeleteSubcommandMixin
from sandwich.core.management.lib.delete import DeleteSubcommandMixinProtocol
from sandwich.core.management.lib.factory import FactoryMixin
from sandwich.core.management.lib.factory import FactoryMixinProtocol
from sandwich.core.management.lib.input import InputMixin
from sandwich.core.management.lib.list import ListSubcommandMixin
from sandwich.core.management.lib.list import ListSubcommandMixinProtocol
from sandwich.core.management.lib.logging import LoggingCommandProtocol
from sandwich.core.management.lib.logging import LoggingMixin
from sandwich.core.management.lib.model import ModelReportMixin
from sandwich.core.management.lib.model import ModelReportMixinProtocol
from sandwich.core.management.lib.report import ReportMixin
from sandwich.core.management.lib.report import ReportMixinProtocol
from sandwich.core.management.lib.subcommand import SubcommandMixin
from sandwich.core.management.lib.subcommand import SubcommandMixinProtocol


class ListCommand[M: Model](  # type: ignore[override]
    ListSubcommandMixin[M],
    ModelReportMixin[M],
    SubcommandMixin,
    ReportMixin,
    InputMixin,
    LoggingMixin,
    BaseCommand,
    ABC,
):
    """A command to simplify listing of model instances. Subclasses must define the properties below."""

    model: type[M]


class ListCommandProtocol[M: Model](
    ListSubcommandMixinProtocol,
    ModelReportMixinProtocol,
    ReportMixinProtocol,
    SubcommandMixinProtocol,
    LoggingCommandProtocol,
    Protocol,
):
    pass


class CreateListDeleteCommand[M: Model](  # type: ignore[override]
    CreateSubcommandMixin,
    ListSubcommandMixin,
    DeleteSubcommandMixin,
    ModelReportMixin,
    SubcommandMixin,
    FactoryMixin,
    ReportMixin,
    InputMixin,
    LoggingMixin,
    BaseCommand,
    ABC,
):
    """
    A command to simplify the creation, listing and deletion of model instances.
    Subclasses must define the properties below.
    """

    model: type[M]
    factory: type[factory.Factory]


class CreateListDeleteCommandProtocol[M: Model](
    CreateSubcommandMixinProtocol,
    ListSubcommandMixinProtocol[M],
    DeleteSubcommandMixinProtocol,
    ModelReportMixinProtocol,
    FactoryMixinProtocol,
    ReportMixinProtocol,
    SubcommandMixinProtocol,
    LoggingCommandProtocol,
    Protocol,
):
    pass
