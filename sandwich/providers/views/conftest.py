"""Shared fixtures for provider views tests."""

import pytest
from django.urls import reverse
from playwright.sync_api import Page

from sandwich.users.models import User


def login(live_server, page: Page, user: User) -> Page:
    """Helper function to log in a user via the login page."""
    page.goto(f"{live_server.url}{reverse('account_login')}")
    page.get_by_role("textbox", name="Email*").click()
    page.get_by_role("textbox", name="Email*").fill(user.email)
    page.get_by_role("textbox", name="Password*").click()
    page.get_by_role("textbox", name="Password*").fill(user.raw_password)  # type: ignore[attr-defined]
    page.get_by_role("checkbox", name="Remember Me").check()
    page.get_by_role("button", name="Sign In").click()
    return page


@pytest.fixture
def provider_page(live_server, page: Page, provider: User) -> Page:
    """Fixture that returns a logged-in provider page for E2E tests."""
    return login(live_server, page, provider)
