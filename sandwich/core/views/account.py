import logging

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from sandwich.core.forms import DeleteConfirmationForm
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


@login_required
def account_delete(request: AuthenticatedHttpRequest) -> HttpResponse:
    logger.info("Accessing account delete", extra={"user_id": request.user.id})

    if request.method == "POST":
        logger.info("Processing account delete form", extra={"user_id": request.user.id})
        form = DeleteConfirmationForm(request.POST, form_action=reverse("core:account_delete"), hx_target="body")
        if not form.is_valid():
            return render(request, "users/account_delete.html", context={"form": form})

        user = request.user
        logout(request)
        user.delete_account()
        logger.info("Account deleted successfully", extra={"user_id": user.id})
        messages.add_message(request, messages.SUCCESS, "Account deleted successfully. We're sorry to see you go.")
        return redirect(reverse("account_login"))

    logger.debug("Rendering account delete form", extra={"user_id": request.user.id})
    form = DeleteConfirmationForm(
        form_action=reverse("core:account_delete"),
        hx_target="body",
    )

    context = {"form": form}
    return render(request, "users/account_delete.html", context)
