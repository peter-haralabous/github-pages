import logging

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.decorators import login_not_required
from django.http import HttpRequest
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from sandwich.core.models.invitation import Invitation
from sandwich.core.models.invitation import InvitationStatus
from sandwich.core.service.invitation_service import accept_patient_invitation

logger = logging.getLogger(__name__)


class InvitationAcceptForm(forms.Form):
    accepted = forms.BooleanField(required=True, label="I accept the invitation")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit"))


@login_not_required
def accept_invite(request: HttpRequest, token: str) -> HttpResponse:
    logger.info(
        "Invitation acceptance attempt",
        extra={
            "has_token": bool(token),
            "is_authenticated": request.user.is_authenticated,
            "user_id": request.user.id if request.user.is_authenticated else None,
        },
    )

    invitation = get_object_or_404(
        Invitation.objects.filter(status=InvitationStatus.PENDING, expires_at__gt=timezone.now()), token=token
    )
    logger.debug(
        "Valid invitation found",
        extra={
            "invitation_id": invitation.id,
            "patient_id": invitation.patient.id,
            "organization_id": invitation.patient.organization.id if invitation.patient.organization else "Unknown",
        },
    )

    if not request.user.is_authenticated:
        logger.info(
            "Rendering public invitation page for unauthenticated user", extra={"invitation_id": invitation.id}
        )
        return render(request, "patient/accept_invite_public.html", context={"invitation": invitation})

    if request.method == "POST":
        logger.info(
            "Processing invitation acceptance form", extra={"invitation_id": invitation.id, "user_id": request.user.id}
        )
        form = InvitationAcceptForm(request.POST)
        if form.is_valid():
            logger.info(
                "Accepting patient invitation",
                extra={
                    "invitation_id": invitation.id,
                    "user_id": request.user.id,
                    "patient_id": invitation.patient.id,
                },
            )
            # TODO: if the user already has patients, they may want to merge one of them with the invited one
            accept_patient_invitation(invitation, request.user)
            logger.info(
                "Invitation accepted successfully",
                extra={
                    "invitation_id": invitation.id,
                    "user_id": request.user.id,
                    "patient_id": invitation.patient.id,
                },
            )
            return HttpResponseRedirect(
                reverse("patients:patient_details", kwargs={"patient_id": invitation.patient.id})
            )
        logger.warning(
            "Invalid invitation acceptance form",
            extra={
                "invitation_id": invitation.id,
                "user_id": request.user.id,
                "form_errors": list(form.errors.keys()),
            },
        )
    else:
        logger.debug(
            "Rendering invitation acceptance form", extra={"invitation_id": invitation.id, "user_id": request.user.id}
        )
        form = InvitationAcceptForm()

    context = {"invitation": invitation, "form": form}
    return render(request, "patient/accept_invite.html", context)
