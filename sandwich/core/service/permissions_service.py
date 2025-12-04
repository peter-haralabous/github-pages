import logging
from dataclasses import dataclass

from django.shortcuts import get_object_or_404
from guardian.shortcuts import get_objects_for_user

from sandwich.core.models.abstract import BaseModel
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.users.models import User

logger = logging.getLogger(__name__)


class ObjectNameCollisionError(ValueError):
    pass


# TODO(MM): A future abstraction to make this into a more useable general func
def get_authorized_object_or_404(user: User, perms: list[str], model: type[BaseModel], *args, **kwargs) -> BaseModel:
    authorized_objects = get_objects_for_user(user, perms, model.objects.all())  # type: ignore[attr-defined]
    return get_object_or_404(authorized_objects, *args, **kwargs)


# Optioinal obj instance param name override
# Rule = tuple[type[BaseModel], str, list[str]] | tuple[type[BaseModel], str, list[str], str]
@dataclass
class ObjPerm:
    """
    model - Model class
    pk_param - View object(s) url pk parameter
    perms - List of permissions strings
    object_name (optional) - Name for the object instance kwarg passed to the view, defaults to class model_name
    """

    model: type[BaseModel]
    pk_param: str
    perms: list[str]
    object_name: str | None = None


def authorize_objects(rules: list[ObjPerm]):
    """
    This decorator extracts id parameters from a view, validates whether the
    user can access the objects based on the permissions passed, and injects
    the verified objects into the view as model instances.

    Consider the following example where we have a view called
    `organization_edit` with the url `organization/<uuid:organization_id>/edit`.

    ```py
    @authorize_objects([
        (Organization, "organization_id", ["view_organization", "change_organization"])
    ])
    def organization_edit(request, organization: Organization):
      ...
    ```
    """

    def decorator(view_func):
        def view_wrapper(request: AuthenticatedHttpRequest, *args, **kwargs):
            objects = {}
            for rule in rules:
                pk = kwargs.pop(rule.pk_param)
                obj = get_authorized_object_or_404(request.user, rule.perms, rule.model, id=pk)

                obj_name = rule.object_name
                if not rule.object_name:
                    obj_name = rule.model._meta.model_name  # noqa: SLF001

                if obj_name in objects:
                    raise ObjectNameCollisionError(f"An object with the name {obj_name} already exists.")

                objects[obj_name] = obj
            return view_func(request, *args, **objects, **kwargs)

        if len(rules) > 0:
            # This attribute is used by `permissioned_views_test` to ensure views
            # are being permissioned.
            setattr(view_wrapper, "authorize_objects", True)  # noqa: B010
        return view_wrapper

    return decorator
