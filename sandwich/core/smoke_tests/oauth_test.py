import pytest
from django.urls import reverse
from playwright.sync_api import Page


@pytest.mark.smoke_test
def test_oauth_redirect(base_url, page: Page):
    """
    Test that the home page displays the Continue as Patient and Continue as Provider buttons
    """

    # Navigate to the home page
    page.goto(f"{base_url}{reverse('account_login')}")

    # Wait for the page to load completely
    page.wait_for_load_state("networkidle")

    page.get_by_role("button", name="Continue with Google").click()

    # Assert we are taken to google login
    page.wait_for_url("**/accounts.google.com/**")
