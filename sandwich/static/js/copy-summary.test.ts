import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { setupCopyButtons } from './copy-summary';

/**
 * Tests for copy-summary functionality
 */

describe('Copy Summary Button', () => {
  let container: HTMLDivElement;
  let mockClipboard: { writeText: ReturnType<typeof vi.fn> };
  let originalClipboard: Clipboard;

  beforeEach(() => {
    // Setup DOM
    container = document.createElement('div');
    document.body.appendChild(container);

    // Save original clipboard and mock it
    originalClipboard = navigator.clipboard;
    mockClipboard = {
      writeText: vi.fn().mockResolvedValue(undefined),
    };
    Object.defineProperty(navigator, 'clipboard', {
      value: mockClipboard,
      writable: true,
      configurable: true,
    });
  });

  afterEach(() => {
    document.body.removeChild(container);
    // Restore original clipboard
    Object.defineProperty(navigator, 'clipboard', {
      value: originalClipboard,
      writable: true,
      configurable: true,
    });
    vi.clearAllMocks();
  });

  it('should copy text to clipboard when button is clicked', async () => {
    // Setup button
    const testText = '<h1>Test Summary</h1><p>Content</p>';
    container.innerHTML = `
      <button class="js-copy-summary" data-copy-text="${testText}">
        Copy Summary
      </button>
    `;

    setupCopyButtons();

    const button =
      container.querySelector<HTMLButtonElement>('.js-copy-summary')!;
    button.click();

    // Wait for async clipboard operation
    await vi.waitFor(() => {
      expect(mockClipboard.writeText).toHaveBeenCalledWith(testText);
    });
  });

  it('should show "Copied!" feedback and disable button temporarily', async () => {
    container.innerHTML = `
      <button class="js-copy-summary" data-copy-text="test">
        Copy Summary
      </button>
    `;

    setupCopyButtons();

    const button =
      container.querySelector<HTMLButtonElement>('.js-copy-summary')!;
    const originalHTML = button.innerHTML;

    button.click();

    await vi.waitFor(() => {
      expect(button.textContent).toBe('Copied!');
      expect(button.disabled).toBe(true);
    });

    // Wait for timeout to restore original state
    await vi.waitFor(
      () => {
        expect(button.innerHTML).toBe(originalHTML);
        expect(button.disabled).toBe(false);
      },
      { timeout: 2500 },
    );
  });

  it('should not copy if data-copy-text is missing', async () => {
    container.innerHTML = `
      <button class="js-copy-summary">
        Copy Summary
      </button>
    `;

    setupCopyButtons();

    const button =
      container.querySelector<HTMLButtonElement>('.js-copy-summary')!;
    button.click();

    await new Promise((resolve) => setTimeout(resolve, 100));

    expect(mockClipboard.writeText).not.toHaveBeenCalled();
  });

  it('should handle clipboard write errors gracefully', async () => {
    const consoleErrorSpy = vi
      .spyOn(console, 'error')
      .mockImplementation(() => {});
    mockClipboard.writeText.mockRejectedValue(
      new Error('Clipboard not available'),
    );

    container.innerHTML = `
      <button class="js-copy-summary" data-copy-text="test">
        Copy Summary
      </button>
    `;

    setupCopyButtons();

    const button =
      container.querySelector<HTMLButtonElement>('.js-copy-summary')!;
    button.click();

    await vi.waitFor(() => {
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Failed to copy text:',
        expect.any(Error),
      );
    });

    consoleErrorSpy.mockRestore();
  });

  it('should not attach duplicate listeners to the same button', async () => {
    container.innerHTML = `
      <button class="js-copy-summary" data-copy-text="test">
        Copy Summary
      </button>
    `;

    // Setup twice
    setupCopyButtons();
    setupCopyButtons();

    const button =
      container.querySelector<HTMLButtonElement>('.js-copy-summary')!;

    // Click once
    button.click();

    await vi.waitFor(() => {
      // Should only be called once despite multiple setups
      expect(mockClipboard.writeText).toHaveBeenCalledTimes(1);
    });
  });

  it('should handle multiple copy buttons on the same page', async () => {
    container.innerHTML = `
      <button class="js-copy-summary" data-copy-text="content1">Copy 1</button>
      <button class="js-copy-summary" data-copy-text="content2">Copy 2</button>
    `;

    setupCopyButtons();

    const buttons =
      container.querySelectorAll<HTMLButtonElement>('.js-copy-summary');

    buttons[0].click();
    await vi.waitFor(() => {
      expect(mockClipboard.writeText).toHaveBeenCalledWith('content1');
    });

    buttons[1].click();
    await vi.waitFor(() => {
      expect(mockClipboard.writeText).toHaveBeenCalledWith('content2');
    });

    expect(mockClipboard.writeText).toHaveBeenCalledTimes(2);
  });
});
