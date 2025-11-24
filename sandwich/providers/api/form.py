import logging
import uuid
from typing import Annotated
from typing import cast

import ninja
from django import forms
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


class SurveyFormInput(forms.ModelForm):
    class Meta:
        model = Form
        fields = ["name", "schema", "organization"]


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
    instance = None
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
        instance = cast(
            "Form", get_authorized_object_or_404(request.user, ["view_form", "change_form"], Form, id=form_id)
        )

    # Validation: Guard against empty title in payload as Form.name is required.
    schema = payload.get("schema")
    name = schema.get("title") if schema else None
    if not name:
        logger.info(
            "Form save failed: form title missing",
            extra={"user_id": request.user.id, "organization_id": organization_id, "payload": payload},
        )
        raise HttpError(400, "Form must include a title: 'General' section missing 'Survey title'")

    form_data = {"name": name, "schema": schema, "organization": organization}

    survey_form = SurveyFormInput(data=form_data, instance=instance)

    if survey_form.is_valid():
        form = survey_form.save()
        logger.info(
            "Form saved successfully",
            extra={
                "user_id": request.user.id,
                "organization_id": organization.id,
                "form_id": form.id,
                "form_name": form.name,
            },
        )
        return FormSavedResponse.success(form=form, message="Form saved successfully")
    errors = survey_form.errors
    logger.warning(
        "Form save failed: Validation Error",
        extra={"user_id": request.user.id, "organization_id": organization.id, "errors": errors},
    )

    first_field = next(iter(errors.keys()))
    first_msg = errors[first_field][0]

    display_msg = first_msg if first_field in ["__all__", "schema"] else f"{first_field.capitalize()}: {first_msg}"

    raise HttpError(400, f"{display_msg}")
