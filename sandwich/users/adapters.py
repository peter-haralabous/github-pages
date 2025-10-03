from __future__ import annotations

import typing
from pathlib import Path

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.apps import apps
from django.conf import settings
from django.core.mail import EmailMessage

from sandwich.core.service.template_service import LoaderDefinitions
from sandwich.core.service.template_service import render

if typing.TYPE_CHECKING:
    from allauth.socialaccount.models import SocialLogin
    from django.http import HttpRequest

    from sandwich.users.models import User


def allauth_loaders() -> LoaderDefinitions:
    allauth_templates = Path(apps.get_app_config("allauth").path) / "templates"
    return [("django.template.loaders.filesystem.Loader", (allauth_templates,))]


class DefaultAccountAdapterProtocol(typing.Protocol):
    def get_from_email(self) -> str: ...


class TemplatedMailMixin:
    """Mixin to add Template email rendering to allauth adapters."""

    def render_mail(
        self: DefaultAccountAdapterProtocol,
        template_prefix: str,
        email: str,
        context: dict[str, typing.Any],
        headers: dict[str, str] | None = None,
    ) -> EmailMessage:
        """
        Renders an email with the given template prefix and context.

        The templates used are "{template_prefix}_subject.txt" and "{template_prefix}_message.txt".

        The templates are looked up using two template loaders:
        - The database loader, looking in the Template model for templates with the given slug
        - The filesystem loader, looking in the "templates" directory of allauth
        """

        context.setdefault("app_url", settings.APP_URL)
        msg = EmailMessage(
            subject=render(
                f"{template_prefix}_subject.txt", context=context, loaders=allauth_loaders(), as_markdown=False
            ).strip(),
            body=render(f"{template_prefix}_message.txt", context=context, loaders=allauth_loaders()),
            from_email=self.get_from_email(),
            to=[email],
            headers=headers or {},
        )
        msg.content_subtype = "html"
        return msg


class AccountAdapter(TemplatedMailMixin, DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)


class SocialAccountAdapter(TemplatedMailMixin, DefaultSocialAccountAdapter):
    def is_open_for_signup(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
    ) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def populate_user(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
        data: dict[str, typing.Any],
    ) -> User:
        """
        Populates user information from social provider info.

        See: https://docs.allauth.org/en/latest/socialaccount/advanced.html#creating-and-populating-user-instances
        """
        user = super().populate_user(request, sociallogin, data)
        if not user.name:
            if name := data.get("name"):
                user.name = name
            elif first_name := data.get("first_name"):
                user.name = first_name
                if last_name := data.get("last_name"):
                    user.name += f" {last_name}"
        return user
