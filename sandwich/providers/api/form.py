import logging
import uuid
from typing import Annotated
from typing import cast

import ninja
from django.db import IntegrityError
from django.http import JsonResponse
from ninja.errors import HttpError
from ninja.security import SessionAuth

from sandwich.core.models.form import Form
from sandwich.core.models.organization import Organization
from sandwich.core.service.permissions_service import get_authorized_object_or_404
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)
router = ninja.Router()
require_login = SessionAuth()


class FormSavedResponse(JsonResponse):
    """
    A custom JsonResponse for saving a form.
    """

    @classmethod
    def success(cls, form: Form, message: str, **kwargs) -> "FormSavedResponse":
        data = {
            "result": "success",
            "message": message,
            "form_id": str(form.id),
        }
        return cls(data, **kwargs)


@router.post("/organization/{organization_id}/save", auth=require_login)
def save_form(
    request: AuthenticatedHttpRequest, organization_id: uuid.UUID, payload: Annotated[dict, ninja.Body(...)]
) -> FormSavedResponse:
    logger.info(
        "Provider API: form save accessed",
        extra={"user_id": request.user.id, "organization_id": organization_id, "payload": payload},
    )
    organization = cast(
        "Organization", get_authorized_object_or_404(request.user, ["create_form"], Organization, id=organization_id)
    )

    # Check payload for form ID to determine create vs. edit (and check form permissions)
    form_id = payload.get("form_id")
    form = None
    if form_id:
        logger.debug(
            "Form ID found in payload, handling save as form edit",
            extra={
                "user_id": request.user.id,
                "organization_id": organization_id,
                "form_id": form_id,
                "payload": payload,
            },
        )
        form = cast("Form", get_authorized_object_or_404(request.user, ["view_form", "change_form"], Form, id=form_id))

    # Validation: Guard against empty title in payload as Form.name is required.
    schema = payload.get("schema")
    name = schema.get("title") if schema else None
    if not name:
        logger.info(
            "Form save failed: form title missing",
            extra={"user_id": request.user.id, "organization_id": organization_id, "payload": payload},
        )
        raise HttpError(400, "Form must include a title: 'General' section missing 'Survey title'")

    try:
        if form_id and form:
            form.name = name
            form.schema = schema
            form.save(update_fields=["name", "schema", "updated_at"])
        else:
            form = Form.objects.create(organization=organization, name=name, schema=schema)
    except IntegrityError as ex:
        logger.info(
            "Form save failed: Form with same name exists in organization",
            extra={
                "user_id": request.user.id,
                "organization_id": organization_id,
                "form_name": name,
                "payload": payload,
            },
        )
        raise HttpError(400, "Form with the same title already exists. Please choose a different title.") from ex

    logger.info(
        "Form saved successfully",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "form_id": form.id,
            "form_name": form.name,  # should not contain PHI.
        },
    )
    return FormSavedResponse.success(form=form, message="Form saved successfully")
