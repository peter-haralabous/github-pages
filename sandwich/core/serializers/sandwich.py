from django.core.serializers.json import Serializer as JsonSerializer
from django_enum import EnumField


class Serializer(JsonSerializer):
    """Custom JSON serializer to handle Sandwich-specific serialization needs."""

    def handle_field(self, obj, field):
        if isinstance(field, EnumField):
            self._current[field.name] = getattr(obj, field.name).value  # type: ignore[attr-defined]
        else:
            super().handle_field(obj, field)
