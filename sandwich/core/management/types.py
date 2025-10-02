from sandwich.core.management.lib.types import model_type
from sandwich.core.models import Template


def template_type(value: str) -> Template:
    return model_type(Template, ["id", "slug"], value)
