from collections.abc import Callable
from typing import Any
from typing import TypeVar

import pydantic
from django.core.management import CommandParser
from pydantic_settings import CliApp
from pydantic_settings import CliSettingsSource

PydanticModel = TypeVar("PydanticModel", bound=pydantic.BaseModel)


class PydanticArgumentsMixin:
    """A management command mixin that provides helpers to add Pydantic models as arguments

    Usage:

        class Person(pydantic.BaseModel):
            name: str

        class Command(BaseCommand, PydanticArgumentsMixin):

            def add_arguments(self, parser: CommandParser) -> None:
                self.add_pydantic_arguments(parser=parser, model=Person)

            def handle(self, *args, **options):  # type: ignore[no-untyped-def]
                person = self.get_pydantic_instance(Person, **kwargs)
                self.stdout.write(f"Hello {person.name}")

        > python manage.py my_command --name Alice
        Hello Alice

    See also: https://docs.pydantic.dev/latest/concepts/pydantic_settings/#integrating-with-existing-parsers
    """

    _settings_source: dict[Any, CliSettingsSource]

    def add_pydantic_arguments(self, parser: CommandParser, model: type[PydanticModel]) -> None:
        """
        Registers the fields of a pydantic model as arguments in the parser and saves the configuration for retrieval

        See: https://docs.pydantic.dev/latest/concepts/pydantic_settings/#creating-cli-applications
        """
        if not hasattr(self, "_settings_source"):
            self._settings_source = {}

        self._settings_source[model] = CliSettingsSource(
            model,
            root_parser=parser,
            cli_implicit_flags=True,
        )

    def get_pydantic_instance(
        self,
        model: type[PydanticModel],
        argument_processors: dict[str, Callable[[Any], Any]] | None = None,
        **kwargs: Any,
    ) -> PydanticModel:
        """Returns an instance of a Pydantic model with the provided keyword arguments"""
        if argument_processors:
            kwargs.update(**{k: argument_processors[k](v) for k, v in kwargs.items() if k in argument_processors})
        return CliApp.run(model, cli_args=kwargs, cli_settings_source=self._settings_source[model])
