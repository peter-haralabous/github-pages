from typing import Any


class VersionMixin:
    """A mixin that provides versioning functionality to a tracked model.

    Based on django-pghistory.
    https://django-pghistory.readthedocs.io/en/3.8.3/event_tracking/
    """

    # This comes from pghistory. mypy is upset this is not declared on the model.
    events: Any

    def get_current_version(self):
        """Return the current snapshot version of the model instance."""
        return self.events.order_by("-pgh_id").first()

    def get_current_version_id(self) -> int:
        """Return the ID of the current version"""
        return self.get_current_version().pgh_id

    def get_version(self, version_id: int):
        """Retrieve a specific version by its ID."""
        return self.events.get(pk=version_id)

    def get_versions(self):
        """Retrieve all versions, including the current one."""
        return self.events.order_by("-pgh_id")

    def get_past_versions(self):
        """Retrieve past versions, excluding the current one."""
        return self.events.order_by("-pgh_id")[1:]

    def get_total_versions(self) -> int:
        """Return the total number of versions for this instance."""
        return self.events.count()

    def restore_to(self, previous_version_id: int):
        """Restore to the previous version specified.

        All fields must be tracked to be able to revert.
        https://django-pghistory.readthedocs.io/en/3.8.3/reversion/

        revert() raises a RuntimeError if the event model doesn't track all fields.
        """
        return self.get_version(previous_version_id).revert()
