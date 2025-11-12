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


class FormCreateResponse(JsonResponse):
    """
    A custom JsonResponse for creating a new form.
    """

    @classmethod
    def success(cls, form: Form, **kwargs) -> "FormCreateResponse":
        data = {
            "result": "success",
            "message": "Form created successfully",
            "form_id": str(form.id),
        }
        return cls(data, **kwargs)


@router.post("/organization/{organization_id}/create", auth=require_login)
def create_form(
    request: AuthenticatedHttpRequest, organization_id: uuid.UUID, payload: Annotated[dict, ninja.Body(...)]
) -> FormCreateResponse:
    logger.info(
        "Provider API: Form create accessed",
        extra={"user_id": request.user.id, "organization_id": organization_id, "payload": payload},
    )
    organization = cast(
        "Organization", get_authorized_object_or_404(request.user, ["create_form"], Organization, id=organization_id)
    )

    # Validation: Guard against empty title in payload as Form.name is required.
    name = payload.get("title", None)
    if not name:
        logger.info(
            "Form creation failed: form title missing in schema",
            extra={"user_id": request.user.id, "organization_id": organization_id},
        )
        raise HttpError(400, "Form must include a title: 'General' section missing 'Survey title'")

    try:
        form = Form.objects.create(organization=organization, name=name, schema=payload)
    except IntegrityError as ex:
        logger.info(
            "Form creation failed: Form with same name exists in organization",
            extra={"user_id": request.user.id, "organization_id": organization_id, "form_name": name},
        )
        raise HttpError(400, "Form with same title already exists. Please choose a different title.") from ex

    logger.info(
        "Form created in organization",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "form_id": form.id,
            "form_name": form.name,  # should not contain PHI.
        },
    )
    return FormCreateResponse.success(form=form)
