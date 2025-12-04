# mypy: disable-error-code="name-defined"
import dataclasses
import logging
from argparse import ArgumentError
from argparse import ArgumentParser
from collections import defaultdict
from collections.abc import Iterable
from string import Template
from typing import Any
from typing import Protocol

import factory.random

from sandwich.core.management.lib.base import BaseCommandProtocol

logger = logging.getLogger(__name__)


def factory_fields(klass: type[factory.Factory]) -> Iterable[str]:
    return klass._meta.declarations.keys()  # noqa: SLF001


@dataclasses.dataclass
class FactoryWrapper:
    factory_class: type[factory.Factory]

    def add_arguments(
        self,
        parser: ArgumentParser,
        help_template: dict[str, Template] | None = None,
    ) -> None:
        help_template_map: defaultdict[str, Template] = defaultdict(
            lambda: Template(r"argument to ${factory} constructor (${field})"),
            **(help_template or {}),
        )
        template_kwargs = {
            "command": str(parser),
            "factory": self.factory_class.__name__,
        }
        parser.add_argument(
            "--count",
            type=int,
            default=0,
            help=Template(r"size for ${factory}.create_batch(size, **kwargs)").safe_substitute(**template_kwargs),
        )
        for field in factory_fields(self.factory_class):
            flag = f"--{field.replace('_', '-')}"
            try:
                parser.add_argument(
                    flag,
                    default=None,
                    help=help_template_map[field].safe_substitute(flag=flag, field=field, **template_kwargs),
                )
            except ArgumentError as ex:
                logger.debug("`%s` could not be added: %s", flag, ex)

    def extract_kwargs(self, **kwargs: Any) -> Any:
        return {field: kwargs[field] for field in factory_fields(self.factory_class) if kwargs.get(field)}

    def factory(self, **kwargs: Any) -> Any:
        return self.factory_class(**self.extract_kwargs(**kwargs))

    def factory_batch(self, size: int = 1, **kwargs: Any) -> Any:
        return self.factory_class.create_batch(size=size, **self.extract_kwargs(**kwargs))

    def handle_factory(self, count: int | None, **kwargs: Any) -> Any:
        if count:
            return self.factory_batch(size=count, **kwargs)
        return [self.factory(**kwargs)]


class FactoryMixinProtocol(Protocol):
    factory: type[factory.Factory]
    default_help_template: Template
    help_template: dict[str, Template]

    def add_factory_arguments(self, parser: ArgumentParser) -> None: ...
    def handle_factory(self, count: int | None, **kwargs: Any) -> Any: ...


class _FactoryMixinProtocol(BaseCommandProtocol, FactoryMixinProtocol, Protocol):
    """A private protocol for FactoryMixin"""

    _factory_wrapper: FactoryWrapper


class FactoryMixin:
    help_template: dict[str, Template] = {}
    factory: type[factory.Factory]
    _factory_wrapper: FactoryWrapper

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._factory_wrapper = FactoryWrapper(self.factory)

    def add_factory_arguments(self: _FactoryMixinProtocol, parser: ArgumentParser) -> None:
        self._factory_wrapper.add_arguments(parser, help_template=self.help_template)

    def handle_factory(self, **kwargs: Any) -> Any:
        return self._factory_wrapper.handle_factory(**kwargs)
