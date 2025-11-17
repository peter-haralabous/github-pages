import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';

import { HtmxLoadingBar } from './htmx-loading-bar';

describe('HtmxLoadingBar', () => {
  let loadingBar: HtmxLoadingBar;

  beforeEach(() => {
    // Ensure custom element is registered
    if (!customElements.get('htmx-loading-bar')) {
      customElements.define('htmx-loading-bar', HtmxLoadingBar as any);
    }

    loadingBar = document.createElement('htmx-loading-bar') as HtmxLoadingBar;
    document.body.appendChild(loadingBar);
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.clearAllMocks();
  });

  it('should be initially hidden', async () => {
    await loadingBar.updateComplete;
    expect(loadingBar.visible).toBe(false);
    expect(loadingBar.error).toBe(false);

    const progressBar = loadingBar.querySelector('.loading-bar');
    expect(progressBar).not.toHaveClass('visible');
  });

  it('should show on htmx:beforeRequest event', async () => {
    const event = new CustomEvent('htmx:beforeRequest');
    document.body.dispatchEvent(event);

    await loadingBar.updateComplete;
    expect(loadingBar.visible).toBe(true);
    expect(loadingBar.error).toBe(false);

    const progressBar = loadingBar.querySelector('.loading-bar');
    expect(progressBar).toHaveClass('visible');
    expect(progressBar).toHaveClass('normal');
  });

  it('should hide on htmx:afterRequest event when no pending requests', async () => {
    // Start a request
    document.body.dispatchEvent(new CustomEvent('htmx:beforeRequest'));
    await loadingBar.updateComplete;
    expect(loadingBar.visible).toBe(true);

    // Complete the request
    document.body.dispatchEvent(
      new CustomEvent('htmx:afterRequest', {
        detail: { successful: true },
      }),
    );
    await loadingBar.updateComplete;
    expect(loadingBar.visible).toBe(false);

    const progressBar = loadingBar.querySelector('.loading-bar');
    expect(progressBar).not.toHaveClass('visible');
  });

  it('should track multiple concurrent requests', async () => {
    // Start first request
    document.body.dispatchEvent(new CustomEvent('htmx:beforeRequest'));
    await loadingBar.updateComplete;
    expect(loadingBar.visible).toBe(true);

    // Start second request
    document.body.dispatchEvent(new CustomEvent('htmx:beforeRequest'));
    await loadingBar.updateComplete;
    expect(loadingBar.visible).toBe(true);

    // Complete first request - should still be visible
    document.body.dispatchEvent(
      new CustomEvent('htmx:afterRequest', {
        detail: { successful: true },
      }),
    );
    await loadingBar.updateComplete;
    expect(loadingBar.visible).toBe(true);

    // Complete second request - should now hide
    document.body.dispatchEvent(
      new CustomEvent('htmx:afterRequest', {
        detail: { successful: true },
      }),
    );
    await loadingBar.updateComplete;
    expect(loadingBar.visible).toBe(false);
  });

  it('should show error state on htmx:responseError', async () => {
    document.body.dispatchEvent(new CustomEvent('htmx:beforeRequest'));
    await loadingBar.updateComplete;

    document.body.dispatchEvent(new CustomEvent('htmx:responseError'));
    await loadingBar.updateComplete;

    expect(loadingBar.visible).toBe(true);
    expect(loadingBar.error).toBe(true);

    const progressBar = loadingBar.querySelector('.loading-bar');
    expect(progressBar).toHaveClass('error');
    expect(progressBar).toHaveClass('visible');
  });

  it('should show error state on htmx:sendError', async () => {
    document.body.dispatchEvent(new CustomEvent('htmx:beforeRequest'));
    await loadingBar.updateComplete;

    document.body.dispatchEvent(new CustomEvent('htmx:sendError'));
    await loadingBar.updateComplete;

    expect(loadingBar.visible).toBe(true);
    expect(loadingBar.error).toBe(true);

    const progressBar = loadingBar.querySelector('.loading-bar');
    expect(progressBar).toHaveClass('error');
  });

  it('should auto-hide error state after timeout', async () => {
    vi.useFakeTimers();

    document.body.dispatchEvent(new CustomEvent('htmx:beforeRequest'));
    document.body.dispatchEvent(new CustomEvent('htmx:responseError'));
    await loadingBar.updateComplete;

    expect(loadingBar.visible).toBe(true);
    expect(loadingBar.error).toBe(true);

    // Fast-forward time past the auto-hide timeout (3 seconds)
    vi.advanceTimersByTime(3000);
    await loadingBar.updateComplete;

    expect(loadingBar.visible).toBe(false);
    expect(loadingBar.error).toBe(false);

    vi.useRealTimers();
  });

  it('should not auto-hide error if new requests are pending', async () => {
    vi.useFakeTimers();

    // Start first request and trigger error
    document.body.dispatchEvent(new CustomEvent('htmx:beforeRequest'));
    document.body.dispatchEvent(new CustomEvent('htmx:responseError'));
    await loadingBar.updateComplete;

    // Start another request before timeout
    document.body.dispatchEvent(new CustomEvent('htmx:beforeRequest'));
    await loadingBar.updateComplete;

    // Fast-forward time past the auto-hide timeout
    vi.advanceTimersByTime(3000);
    await loadingBar.updateComplete;

    // Should still be visible because we have a pending request
    expect(loadingBar.visible).toBe(true);

    vi.useRealTimers();
  });

  it('should clear error state on successful htmx:afterSwap', async () => {
    document.body.dispatchEvent(new CustomEvent('htmx:beforeRequest'));
    document.body.dispatchEvent(new CustomEvent('htmx:responseError'));
    await loadingBar.updateComplete;

    expect(loadingBar.error).toBe(true);

    document.body.dispatchEvent(new CustomEvent('htmx:afterSwap'));
    await loadingBar.updateComplete;

    expect(loadingBar.visible).toBe(false);
    expect(loadingBar.error).toBe(false);
  });

  it('should render with correct ARIA attributes', async () => {
    await loadingBar.updateComplete;
    const progressBar = loadingBar.querySelector('[role="progressbar"]');
    expect(progressBar).toBeTruthy();
    expect(progressBar?.getAttribute('aria-live')).toBe('polite');
    expect(progressBar?.getAttribute('aria-busy')).toBe('false');
  });

  it('should update aria-busy when visible', async () => {
    document.body.dispatchEvent(new CustomEvent('htmx:beforeRequest'));
    await loadingBar.updateComplete;

    const progressBar = loadingBar.querySelector('[role="progressbar"]');
    expect(progressBar?.getAttribute('aria-busy')).toBe('true');
  });

  it('should render progress-inner element', async () => {
    await loadingBar.updateComplete;
    const progressInner = loadingBar.querySelector('.progress-inner');
    expect(progressInner).toBeTruthy();
  });

  it('should handle rapid request/response cycles', async () => {
    // Simulate rapid fire of requests and responses
    for (let i = 0; i < 5; i++) {
      document.body.dispatchEvent(new CustomEvent('htmx:beforeRequest'));
    }

    await loadingBar.updateComplete;
    expect(loadingBar.visible).toBe(true);

    // Complete all requests
    for (let i = 0; i < 5; i++) {
      document.body.dispatchEvent(
        new CustomEvent('htmx:afterRequest', {
          detail: { successful: true },
        }),
      );
    }

    await loadingBar.updateComplete;
    expect(loadingBar.visible).toBe(false);
  });

  it('should properly cleanup event listeners on disconnect', () => {
    const removeEventListenerSpy = vi.spyOn(
      document.body,
      'removeEventListener',
    );

    loadingBar.remove();

    expect(removeEventListenerSpy).toHaveBeenCalledWith(
      'htmx:beforeRequest',
      expect.any(Function),
    );
    expect(removeEventListenerSpy).toHaveBeenCalledWith(
      'htmx:afterRequest',
      expect.any(Function),
    );
    expect(removeEventListenerSpy).toHaveBeenCalledWith(
      'htmx:responseError',
      expect.any(Function),
    );
    expect(removeEventListenerSpy).toHaveBeenCalledWith(
      'htmx:sendError',
      expect.any(Function),
    );
    expect(removeEventListenerSpy).toHaveBeenCalledWith(
      'htmx:afterSwap',
      expect.any(Function),
    );
  });

  it('should never have negative request count', async () => {
    // Try to complete requests without starting any
    document.body.dispatchEvent(
      new CustomEvent('htmx:afterRequest', {
        detail: { successful: true },
      }),
    );
    await loadingBar.updateComplete;

    // Request count should be clamped at 0, not negative
    expect((loadingBar as any).requestCount).toBe(0);

    // Should work normally after this
    document.body.dispatchEvent(new CustomEvent('htmx:beforeRequest'));
    await loadingBar.updateComplete;
    expect(loadingBar.visible).toBe(true);
    expect((loadingBar as any).requestCount).toBe(1);
  });

  it('should use light DOM (not shadow DOM)', () => {
    // Check that the component uses light DOM
    expect(loadingBar.shadowRoot).toBeNull();
    expect(loadingBar.querySelector('.loading-bar')).toBeTruthy();
  });
});
