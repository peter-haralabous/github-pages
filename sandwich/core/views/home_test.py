import pytest
from django.urls import reverse
from playwright.sync_api import Page


@pytest.mark.e2e
def test_home_page_buttons(live_server, page: Page):
    """
    Test that the home page displays the Continue as Patient and Continue as Provider buttons
    """
    # Navigate to the home page
    page.goto(f"{live_server.url}{reverse('core:home')}")

    # Wait for the page to load completely
    page.wait_for_load_state("networkidle")

    # Check that the HealthConnect logo is present
    logo = page.locator("text=HealthConnect")
    assert logo.is_visible()

    # Check that the Continue as Patient button is present and visible
    patient_button = page.get_by_text("Continue as Patient")
    assert patient_button.is_visible()

    # Check that the Continue as Provider button is present and visible
    provider_button = page.get_by_text("Continue as Provider")
    assert provider_button.is_visible()

    # A link on our homepage that takes the user to our internal privacy policy page
    privacy_link = page.locator("a", has_text="Privacy Policy")
    assert privacy_link.is_visible()
    assert privacy_link.get_attribute("target") == "_blank"
    assert privacy_link.get_attribute("href") == "/policy/privacy-notice/"

    # Click the link and check that a new tab opens with the correct URL
    with page.expect_popup() as popup_info:
        privacy_link.click()
    popup = popup_info.value
    popup.wait_for_load_state("domcontentloaded")
    assert "/policy/privacy-notice" in popup.url


@pytest.mark.e2e
def test_home_page_has_webpack_bundle(live_server, page: Page):
    """
    Smoke test that a webpack-built bundle is included and loaded on the home page.
    """
    page.goto(f"{live_server.url}{reverse('core:home')}")
    page.wait_for_load_state("networkidle")
    page.set_default_timeout(3000)

    # Wait for the bundle link rendered by {% render_bundle 'project' 'css' %}
    # link elements are not visible, so wait for it to be attached to the DOM.
    page.wait_for_selector("#global_styles", state="attached")

    # Check that at least one stylesheet with a webpack_bundles href has accessible CSS rules.
    expr = (
        "() => Array.from(document.styleSheets).some(s => {"
        " try { return s.href && s.href.includes('webpack_bundles') && s.cssRules && s.cssRules.length > 0 }"
        " catch (e) { return false }"
        " })"
    )

    # Wait for the stylesheet to be parsed.
    page.wait_for_function(expr)
    has_loaded_webpack_css = page.evaluate(expr)
    assert has_loaded_webpack_css, "Project CSS bundle not parsed/loaded into document.styleSheets"
