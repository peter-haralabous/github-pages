import argparse

from django.core.exceptions import ValidationError
from django.db.models import Model


def model_type[M: Model](model: type[M], fields: list[str], string: str) -> M:
    """Convert a string to a model instance by searching for it in the specified fields."""
    for field in fields:
        try:
            return model._default_manager.get(**{field: string})  # noqa: SLF001
        except model.MultipleObjectsReturned as exc_info:  # type: ignore[attr-defined]
            msg = f"{model.__name__} has multiple instances with {field}={string}"
            raise argparse.ArgumentTypeError(msg) from exc_info
        except (model.DoesNotExist, ValidationError, ValueError):  # type: ignore[attr-defined]
            pass
    msg = f"No {model.__name__} with {string} in {', '.join(fields)}"
    raise argparse.ArgumentTypeError(msg)
