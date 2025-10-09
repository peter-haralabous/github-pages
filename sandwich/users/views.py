import logging

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import RedirectView
from django.views.generic import UpdateView

from sandwich.core.models import Consent
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.users.forms import AccountDeleteForm
from sandwich.users.models import User

logger = logging.getLogger(__name__)


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "id"
    slug_url_kwarg = "id"

    def get(self, request, *args, **kwargs):
        logger.info(
            "Accessing user detail view", extra={"user_id": request.user.id, "target_user_id": kwargs.get("id")}
        )
        return super().get(request, *args, **kwargs)


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self) -> str:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user.get_absolute_url()

    def get_object(self, queryset: QuerySet | None = None) -> User:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user

    def get(self, request, *args, **kwargs):
        logger.info("Accessing user update form", extra={"user_id": request.user.id})
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logger.info("Processing user update form", extra={"user_id": request.user.id})
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        logger.info("User profile updated successfully", extra={"user_id": self.request.user.id})
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning(
            "Invalid user update form",
            extra={"user_id": self.request.user.id, "form_errors": list(form.errors.keys())},
        )
        return super().form_invalid(form)


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self) -> str:
        logger.debug("Redirecting to user detail", extra={"user_id": self.request.user.pk})
        return reverse("users:detail", kwargs={"pk": self.request.user.pk})


user_redirect_view = UserRedirectView.as_view()


@login_required
def legal_view(request: AuthenticatedHttpRequest) -> HttpResponse:
    consents = Consent.objects.for_user(request.user)

    if len(consents) == 0:
        logger.critical("User has no consented policies", extra={"user_id": request.user.pk})

    return render(
        request,
        "users/legal.html",
        {
            "consents": consents,
        },
    )


@login_required
def account_delete(request: AuthenticatedHttpRequest) -> HttpResponse:
    logger.info("Accessing account delete", extra={"user_id": request.user.id})

    if request.method == "POST":
        logger.info("Processing account delete form", extra={"user_id": request.user.id})
        form = AccountDeleteForm(request.POST)
        if not form.is_valid():
            return render(request, "users/account_delete.html", context={"form": form})

        user = request.user
        logout(request)
        user.delete_account()
        logger.info("Account deleted successfully", extra={"user_id": request.user.id})
        # TODO: send them to a "we're sorry to see you go" page instead?
        return redirect(reverse("account_login"))

    logger.debug("Rendering account delete form", extra={"user_id": request.user.id})
    form = AccountDeleteForm()

    context = {"form": form}
    return render(request, "users/account_delete.html", context)
