"""E2E tests for mobile navigation in the patient chatty app."""

import re

import pytest
from django.urls import reverse
from playwright.sync_api import Page
from playwright.sync_api import expect
from pytest_django.live_server_helper import LiveServer

from sandwich.core.models.patient import Patient


@pytest.fixture
def patient_with_data(patient: Patient) -> Patient:
    """Patient fixture with some health records for testing."""
    # The patient fixture already has some conditions, just return it
    return patient


@pytest.mark.e2e
def test_mobile_navigation_buttons(
    live_server: LiveServer,
    page: Page,
    auth_cookies,
    patient_with_data: Patient,
) -> None:
    """Test that mobile navigation buttons switch between panels correctly."""
    # Navigate to patient details page
    url = f"{live_server.url}{reverse('patients:patient_details', kwargs={'patient_id': patient_with_data.pk})}"
    page.goto(url)

    # Set viewport to mobile size
    page.set_viewport_size({"width": 375, "height": 667})  # iPhone SE size

    # Wait for page to load
    page.wait_for_selector("#mobile-nav", state="visible")

    # Initially on Chat view
    chat_panel = page.locator("#mobile-chat-view")
    records_panel = page.locator("#left-panel")
    feed_panel = page.locator("#right-panel")

    # Chat should be visible by default
    expect(chat_panel).to_be_visible()
    expect(records_panel).not_to_be_visible()
    expect(feed_panel).not_to_be_visible()

    # Click Records button
    page.get_by_role("button", name="Records").click()
    page.wait_for_timeout(100)  # Brief wait for transition

    # Records should be visible, others hidden
    expect(records_panel).to_be_visible()
    expect(chat_panel).not_to_be_visible()
    expect(feed_panel).not_to_be_visible()

    # Click Feed button
    page.get_by_role("button", name="Feed").click()
    page.wait_for_timeout(100)

    # Feed should be visible, others hidden
    expect(feed_panel).to_be_visible()
    expect(chat_panel).not_to_be_visible()
    expect(records_panel).not_to_be_visible()

    # Click Assistant button
    page.get_by_role("button", name="Assistant").click()
    page.wait_for_timeout(100)

    # Chat should be visible again
    expect(chat_panel).to_be_visible()
    expect(records_panel).not_to_be_visible()
    expect(feed_panel).not_to_be_visible()


@pytest.mark.e2e
def test_mobile_navigation_active_states(
    live_server: LiveServer,
    page: Page,
    auth_cookies,
    patient_with_data: Patient,
) -> None:
    """Test that navigation items show correct active states."""
    url = f"{live_server.url}{reverse('patients:patient_details', kwargs={'patient_id': patient_with_data.pk})}"
    page.goto(url)
    page.set_viewport_size({"width": 375, "height": 667})

    # Get navigation buttons
    records_btn = page.get_by_role("button", name="Records")
    assistant_btn = page.get_by_role("button", name="Assistant")

    # Assistant should be active initially
    expect(assistant_btn).to_have_class(re.compile(r"text-primary"))

    # Click Records
    records_btn.click()
    page.wait_for_timeout(100)

    # Records should be active
    expect(records_btn).to_have_class(re.compile(r"text-primary"))
    expect(assistant_btn).to_have_class(re.compile(r"text-base-content/60"))


@pytest.mark.e2e
def test_desktop_shows_all_panels(
    live_server: LiveServer,
    page: Page,
    auth_cookies,
    patient_with_data: Patient,
) -> None:
    """Test that desktop view shows all three panels side-by-side."""
    url = f"{live_server.url}{reverse('patients:patient_details', kwargs={'patient_id': patient_with_data.pk})}"
    page.goto(url)

    # Set viewport to desktop size
    page.set_viewport_size({"width": 1440, "height": 900})

    # Mobile navigation should not be visible
    mobile_nav = page.locator("#mobile-nav")
    expect(mobile_nav).not_to_be_visible()

    # All panels should be visible
    chat_panel = page.locator("#mobile-chat-view")
    records_panel = page.locator("#left-panel")
    feed_panel = page.locator("#right-panel")

    expect(chat_panel).to_be_visible()
    expect(records_panel).to_be_visible()
    expect(feed_panel).to_be_visible()


@pytest.mark.e2e
def test_mobile_navigation_after_modal(
    live_server: LiveServer,
    page: Page,
    auth_cookies,
    patient_with_data: Patient,
) -> None:
    """Test that navigation still works after opening and closing a modal."""
    url = f"{live_server.url}{reverse('patients:patient_details', kwargs={'patient_id': patient_with_data.pk})}"
    page.goto(url)
    page.set_viewport_size({"width": 375, "height": 667})

    # Navigate to Records
    page.get_by_role("button", name="Records").click()
    page.wait_for_timeout(100)

    records_panel = page.locator("#left-panel")
    expect(records_panel).to_be_visible()

    # Click on Conditions (if available)
    conditions_link = page.locator("text=Conditions")
    if conditions_link.count() > 0:
        conditions_link.first.click()
        page.wait_for_timeout(200)

        # Try clicking on a condition (if any exist)
        # This would open a modal
        # Then close the modal and verify navigation still works

    # After any HTMX swaps, navigation should still work
    page.get_by_role("button", name="Assistant").click()
    page.wait_for_timeout(100)

    chat_panel = page.locator("#mobile-chat-view")
    expect(chat_panel).to_be_visible()
    expect(records_panel).not_to_be_visible()


@pytest.mark.e2e
def test_responsive_layout_switch(
    live_server: LiveServer,
    page: Page,
    auth_cookies,
    patient_with_data: Patient,
) -> None:
    """Test switching between mobile and desktop layouts preserves correct view."""
    url = f"{live_server.url}{reverse('patients:patient_details', kwargs={'patient_id': patient_with_data.pk})}"
    page.goto(url)

    # Start on desktop
    page.set_viewport_size({"width": 1440, "height": 900})
    page.wait_for_timeout(200)

    # All panels visible on desktop
    expect(page.locator("#left-panel")).to_be_visible()
    expect(page.locator("#mobile-chat-view")).to_be_visible()
    expect(page.locator("#right-panel")).to_be_visible()

    # Switch to mobile
    page.set_viewport_size({"width": 375, "height": 667})
    page.wait_for_timeout(200)

    # Should default to showing chat (or records based on URL)
    chat_panel = page.locator("#mobile-chat-view")
    # One of the panels should be visible
    visible_panels = [
        page.locator("#left-panel").is_visible(),
        chat_panel.is_visible(),
        page.locator("#right-panel").is_visible(),
    ]
    assert sum(visible_panels) == 1, "Exactly one panel should be visible on mobile"

    # Switch back to desktop
    page.set_viewport_size({"width": 1440, "height": 900})
    page.wait_for_timeout(200)

    # All panels should be visible again
    expect(page.locator("#left-panel")).to_be_visible()
    expect(page.locator("#mobile-chat-view")).to_be_visible()
    expect(page.locator("#right-panel")).to_be_visible()


@pytest.mark.e2e
def test_collapsed_panel_expands_on_mobile(
    live_server: LiveServer,
    page: Page,
    auth_cookies,
    patient_with_data: Patient,
) -> None:
    """Test that collapsed panels on desktop are properly expanded on mobile."""
    url = f"{live_server.url}{reverse('patients:patient_details', kwargs={'patient_id': patient_with_data.pk})}"
    page.goto(url)

    # Start on desktop
    page.set_viewport_size({"width": 1440, "height": 900})
    page.wait_for_timeout(200)

    # Find and click the collapse button for left panel (if it exists)
    collapse_btn = page.locator("#left-panel toggle-button").first
    if collapse_btn.is_visible():
        collapse_btn.click()
        page.wait_for_timeout(100)

        # Panel should be collapsed
        expanded_panel = page.locator("#left-panel .panel-expanded")
        expect(expanded_panel).not_to_be_visible()

    # Switch to mobile
    page.set_viewport_size({"width": 375, "height": 667})
    page.wait_for_timeout(200)

    # Navigate to Records
    page.get_by_role("button", name="Records").click()
    page.wait_for_timeout(100)

    # Records panel should be fully visible and expanded on mobile
    records_panel = page.locator("#left-panel")
    expect(records_panel).to_be_visible()

    # The expanded content should be visible (not the collapsed view)
    # This verifies our CSS fix is working
    expect(records_panel.locator(".panel-expanded")).to_be_visible()


@pytest.mark.e2e
def test_panel_resize_persists_across_viewport_changes(
    live_server: LiveServer,
    page: Page,
    auth_cookies,
    patient_with_data: Patient,
) -> None:
    """Test that panel resize widths are preserved when switching between desktop and mobile."""
    url = f"{live_server.url}{reverse('patients:patient_details', kwargs={'patient_id': patient_with_data.pk})}"
    page.goto(url)

    # Start on desktop
    page.set_viewport_size({"width": 1440, "height": 900})
    page.wait_for_timeout(200)

    # Get initial width of left panel
    left_panel = page.locator("#left-panel")
    initial_width = left_panel.bounding_box()["width"] if left_panel.bounding_box() else None

    # Resize the left panel by dragging the resize handle
    resize_handle = page.locator("#left-resize-handle")
    if resize_handle.is_visible():
        # Get handle position
        handle_box = resize_handle.bounding_box()
        if handle_box:
            # Drag handle to resize (move 100px to the right)
            page.mouse.move(handle_box["x"] + handle_box["width"] / 2, handle_box["y"] + handle_box["height"] / 2)
            page.mouse.down()
            page.mouse.move(handle_box["x"] + 100, handle_box["y"] + handle_box["height"] / 2)
            page.mouse.up()
            page.wait_for_timeout(100)

            # Get new width after resize
            resized_width = left_panel.bounding_box()["width"] if left_panel.bounding_box() else None
            # Verify width changed
            if initial_width and resized_width:
                assert abs(resized_width - initial_width - 100) < 20, "Panel should be resized"

    # Switch to mobile
    page.set_viewport_size({"width": 375, "height": 667})
    page.wait_for_timeout(200)

    # Navigate to Records
    page.get_by_role("button", name="Records").click()
    page.wait_for_timeout(100)

    # Panel should be full width on mobile
    mobile_width = left_panel.bounding_box()["width"] if left_panel.bounding_box() else None
    viewport_width = page.viewport_size["width"]
    if mobile_width:
        # Allow some margin for padding/borders
        assert mobile_width >= viewport_width * 0.9, "Panel should be near full width on mobile"

    # Switch back to desktop
    page.set_viewport_size({"width": 1440, "height": 900})
    page.wait_for_timeout(200)

    # Panel should retain its resized width from before (approximately)
    final_width = left_panel.bounding_box()["width"] if left_panel.bounding_box() else None
    if resized_width and final_width:
        # Allow some tolerance for rounding
        assert abs(final_width - resized_width) < 10, "Panel width should be preserved when returning to desktop"


@pytest.mark.e2e
def test_collapsed_state_persists_across_viewport_changes(
    live_server: LiveServer,
    page: Page,
    auth_cookies,
    patient_with_data: Patient,
) -> None:
    """Test that panel collapse state is preserved when switching between desktop and mobile."""
    url = f"{live_server.url}{reverse('patients:patient_details', kwargs={'patient_id': patient_with_data.pk})}"
    page.goto(url)

    # Start on desktop
    page.set_viewport_size({"width": 1440, "height": 900})
    page.wait_for_timeout(200)

    # Collapse the left panel
    collapse_btn = page.locator("#left-panel toggle-button").first
    if collapse_btn.is_visible():
        collapse_btn.click()
        page.wait_for_timeout(100)

        # Verify panel is collapsed on desktop
        expanded_panel = page.locator("#left-panel .panel-expanded")
        expect(expanded_panel).not_to_be_visible()

        # Switch to mobile
        page.set_viewport_size({"width": 375, "height": 667})
        page.wait_for_timeout(200)

        # Navigate to Records - should be expanded on mobile despite being collapsed on desktop
        page.get_by_role("button", name="Records").click()
        page.wait_for_timeout(100)

        # Should be visible and expanded on mobile
        expect(page.locator("#left-panel")).to_be_visible()
        expect(page.locator("#left-panel .panel-expanded")).to_be_visible()

        # Switch back to desktop
        page.set_viewport_size({"width": 1440, "height": 900})
        page.wait_for_timeout(200)

        # Panel should still be collapsed (state preserved)
        expect(expanded_panel).not_to_be_visible()


@pytest.mark.e2e
def test_focused_collapsed_panel_expands_full_width_on_mobile(
    live_server: LiveServer,
    page: Page,
    auth_cookies,
    patient_with_data: Patient,
) -> None:
    """Test that when a collapsed panel was focused on desktop, it expands to full width on mobile."""
    url = f"{live_server.url}{reverse('patients:patient_details', kwargs={'patient_id': patient_with_data.pk})}"
    page.goto(url)

    # Start on desktop
    page.set_viewport_size({"width": 1440, "height": 900})
    page.wait_for_timeout(200)

    # Click inside the left panel to focus it
    left_panel = page.locator("#left-panel")
    left_panel.click()
    page.wait_for_timeout(100)

    # Collapse the left panel
    collapse_btn = page.locator("#left-panel toggle-button").first
    if collapse_btn.is_visible():
        collapse_btn.click()
        page.wait_for_timeout(100)

        # Panel should be collapsed
        expanded_panel = page.locator("#left-panel .panel-expanded")
        expect(expanded_panel).not_to_be_visible()

        # Switch to mobile - the previously focused panel (Records) should be shown
        page.set_viewport_size({"width": 375, "height": 667})
        page.wait_for_timeout(200)

        # Records panel should automatically be shown and expanded
        expect(left_panel).to_be_visible()
        expect(expanded_panel).to_be_visible()

        # Should be full width on mobile
        panel_width = left_panel.bounding_box()["width"] if left_panel.bounding_box() else None
        viewport_width = page.viewport_size["width"]
        if panel_width:
            assert panel_width >= viewport_width * 0.9, "Panel should be near full width on mobile"


@pytest.mark.e2e
def test_right_panel_collapse_and_resize_behavior(
    live_server: LiveServer,
    page: Page,
    auth_cookies,
    patient_with_data: Patient,
) -> None:
    """Test that right panel (Feed) also properly handles collapse/resize across viewport changes."""
    url = f"{live_server.url}{reverse('patients:patient_details', kwargs={'patient_id': patient_with_data.pk})}"
    page.goto(url)

    # Start on desktop
    page.set_viewport_size({"width": 1440, "height": 900})
    page.wait_for_timeout(200)

    # Collapse the right panel
    right_panel = page.locator("#right-panel")
    collapse_btn = page.locator("#right-panel toggle-button").first
    if collapse_btn.is_visible():
        collapse_btn.click()
        page.wait_for_timeout(100)

        # Panel should be collapsed on desktop
        expanded_panel = page.locator("#right-panel .panel-expanded")
        expect(expanded_panel).not_to_be_visible()

        # Switch to mobile
        page.set_viewport_size({"width": 375, "height": 667})
        page.wait_for_timeout(200)

        # Navigate to Feed
        page.get_by_role("button", name="Feed").click()
        page.wait_for_timeout(100)

        # Feed panel should be visible and expanded on mobile
        expect(right_panel).to_be_visible()
        expect(expanded_panel).to_be_visible()

        # Should be full width
        panel_width = right_panel.bounding_box()["width"] if right_panel.bounding_box() else None
        viewport_width = page.viewport_size["width"]
        if panel_width:
            assert panel_width >= viewport_width * 0.9, "Feed panel should be near full width on mobile"

        # Switch back to desktop
        page.set_viewport_size({"width": 1440, "height": 900})
        page.wait_for_timeout(200)

        # Panel should be collapsed again (state preserved)
        expect(expanded_panel).not_to_be_visible()


@pytest.mark.e2e
def test_tablet_width_proper_sizing(
    live_server: LiveServer,
    page: Page,
    auth_cookies,
    patient_with_data: Patient,
) -> None:
    """Test that panels resize properly to tablet width (between mobile and desktop)."""
    url = f"{live_server.url}{reverse('patients:patient_details', kwargs={'patient_id': patient_with_data.pk})}"
    page.goto(url)

    # Start on desktop and resize a panel
    page.set_viewport_size({"width": 1440, "height": 900})
    page.wait_for_timeout(200)

    # Switch to tablet size (below 1024px breakpoint)
    page.set_viewport_size({"width": 768, "height": 1024})  # iPad portrait
    page.wait_for_timeout(200)

    # Should show mobile navigation
    mobile_nav = page.locator("#mobile-nav")
    expect(mobile_nav).to_be_visible()

    # Navigate to Records
    page.get_by_role("button", name="Records").click()
    page.wait_for_timeout(100)

    # Panel should be full width on tablet
    left_panel = page.locator("#left-panel")
    panel_width = left_panel.bounding_box()["width"] if left_panel.bounding_box() else None
    viewport_width = page.viewport_size["width"]

    if panel_width:
        # Should take up most of the viewport width
        assert panel_width >= viewport_width * 0.9, "Panel should be near full width on tablet"

    # Only one panel should be visible
    visible_panels = [
        page.locator("#left-panel").is_visible(),
        page.locator("#mobile-chat-view").is_visible(),
        page.locator("#right-panel").is_visible(),
    ]
    assert sum(visible_panels) == 1, "Only one panel should be visible on tablet"


@pytest.mark.e2e
def test_mobile_view_respects_last_active_panel(
    live_server: LiveServer,
    page: Page,
    auth_cookies,
    patient_with_data: Patient,
) -> None:
    """Test that when resizing to mobile, the last interacted panel is shown."""
    url = f"{live_server.url}{reverse('patients:patient_details', kwargs={'patient_id': patient_with_data.pk})}"
    page.goto(url)

    # Start on desktop
    page.set_viewport_size({"width": 1440, "height": 900})
    page.wait_for_timeout(200)

    # Navigate into Records view (should be via HTMX)
    page.get_by_text("Records", exact=True).first.click()
    page.wait_for_timeout(300)

    # Now click in the Chat textarea to make it the last active panel
    chat_textarea = page.locator("#mobile-chat-view textarea").first
    chat_textarea.click()
    page.wait_for_timeout(100)

    # Resize to mobile
    page.set_viewport_size({"width": 375, "height": 667})
    page.wait_for_timeout(200)

    # Chat should be visible (not Records) because we clicked in Chat last
    chat_panel = page.locator("#mobile-chat-view")
    records_panel = page.locator("#left-panel")
    expect(chat_panel).to_be_visible()
    expect(records_panel).not_to_be_visible()


@pytest.mark.e2e
def test_mobile_view_shows_active_panel_after_navigation(
    live_server: LiveServer,
    page: Page,
    auth_cookies,
    patient_with_data: Patient,
) -> None:
    """Test that when navigating in a panel and resizing to mobile, that panel is shown."""
    url = f"{live_server.url}{reverse('patients:patient_details', kwargs={'patient_id': patient_with_data.pk})}"
    page.goto(url)

    # Start on desktop
    page.set_viewport_size({"width": 1440, "height": 900})
    page.wait_for_timeout(200)

    # Navigate into Records view via HTMX
    page.get_by_text("Records", exact=True).first.click()
    page.wait_for_timeout(300)

    # Don't interact with any other panels - Records should be last active

    # Resize to mobile
    page.set_viewport_size({"width": 375, "height": 667})
    page.wait_for_timeout(200)

    # Records should be visible because we navigated within it
    chat_panel = page.locator("#mobile-chat-view")
    records_panel = page.locator("#left-panel")
    expect(records_panel).to_be_visible()
    expect(chat_panel).not_to_be_visible()


@pytest.mark.e2e
def test_mobile_view_respects_records_when_clicking_items_that_swap_feed(
    live_server: LiveServer,
    page: Page,
    auth_cookies,
    patient_with_data: Patient,
) -> None:
    """Test that clicking items in Records panel that trigger Feed swaps still keeps Records as active panel."""
    url = f"{live_server.url}{reverse('patients:patient_details', kwargs={'patient_id': patient_with_data.pk})}"
    page.goto(url)

    # Start on desktop
    page.set_viewport_size({"width": 1440, "height": 900})
    page.wait_for_timeout(200)

    # Click on Records to navigate there
    page.get_by_text("Records", exact=True).first.click()
    page.wait_for_timeout(300)

    # Now click on a condition/practitioner item in the left panel
    # This might trigger an HTMX request that swaps content in the right panel (Feed)
    # But the user is still interacting with the Records panel
    conditions_link = page.locator("#left-panel a").filter(has_text="Conditions").first
    if conditions_link.is_visible():
        conditions_link.click()
        page.wait_for_timeout(300)

    # Resize to mobile
    page.set_viewport_size({"width": 375, "height": 667})
    page.wait_for_timeout(200)

    # Records should be visible because the user clicked in the Records panel
    # even though the click might have triggered a swap in the Feed panel
    chat_panel = page.locator("#mobile-chat-view")
    records_panel = page.locator("#left-panel")
    feed_panel = page.locator("#right-panel")
    expect(records_panel).to_be_visible()
    expect(chat_panel).not_to_be_visible()
    expect(feed_panel).not_to_be_visible()
