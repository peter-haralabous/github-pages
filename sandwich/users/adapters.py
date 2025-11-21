from __future__ import annotations

import typing

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.core.mail import EmailMessage
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string

from sandwich.core.service.markdown_service import markdown_to_html

if typing.TYPE_CHECKING:
    from allauth.socialaccount.models import SocialLogin
    from django.http import HttpRequest

    from sandwich.users.models import User


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def render_mail(
        self,
        template_prefix: str,
        email: str,
        context: dict[str, typing.Any],
        headers: dict[str, str] | None = None,
    ) -> EmailMessage:
        """
        Renders an email with the given template prefix and context.

        The templates used are "{template_prefix}_subject.txt" and "{template_prefix}_message.txt".
        """

        # v -- this is copied directly from the superclass implementation
        to = [email] if isinstance(email, str) else email
        subject: str = render_to_string(f"{template_prefix}_subject.txt", context)
        subject = " ".join(subject.splitlines()).strip()
        subject = self.format_email_subject(subject)
        from_email = self.get_from_email()
        # ^ -- this is copied directly from the superclass implementation

        context.setdefault("app_url", settings.APP_URL)
        try:
            # if we have a HTML template, use it
            body = render_to_string(f"{template_prefix}_message.html", context=context)
        except TemplateDoesNotExist:
            # but if it doesn't exist, render the allauth default text and wrap it in an HTML envelope
            text_body = render_to_string(f"{template_prefix}_message.txt", context=context)
            body = render_to_string(
                "email/wrap_text_email.html",
                context={
                    **context,
                    "subject": subject,
                    "body": markdown_to_html(text_body, options={"linkify": "true"}),
                },
            )

        msg = EmailMessage(
            subject=subject,
            body=body,
            from_email=from_email,
            to=to,
            headers=headers or {},
        )
        msg.content_subtype = "html"
        return msg


class SocialAccountAdapter(DefaultSocialAccountAdapter):
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
