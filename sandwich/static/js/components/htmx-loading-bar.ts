import { LitElement, html } from 'lit';
import { customElement, property } from 'lit/decorators.js';

/**
 * GitHub-style loading bar for HTMX requests.
 *
 * Shows a thin progress bar at the top of the page during HTMX requests.
 * Displays error state with increased height and danger styling on failures.
 * Tracks multiple concurrent requests and only hides when all complete.
 *
 * Usage:
 * <htmx-loading-bar></htmx-loading-bar>
 *
 * Place once in base template - automatically hooks into HTMX lifecycle events.
 */
@customElement('htmx-loading-bar')
export class HtmxLoadingBar extends LitElement {
  @property({ type: Boolean }) accessor visible = false;
  @property({ type: Boolean }) accessor error = false;

  private requestCount = 0;

  connectedCallback() {
    super.connectedCallback();
    this.setupHtmxListeners();
  }

  createRenderRoot(): HTMLElement {
    return this;
  }

  private setupHtmxListeners() {
    // Show loading bar when HTMX request starts
    document.body.addEventListener(
      'htmx:beforeRequest',
      this.handleBeforeRequest,
    );

    // Hide loading bar when HTMX request completes successfully
    document.body.addEventListener(
      'htmx:afterRequest',
      this.handleAfterRequest,
    );

    // Show error state on request failures
    document.body.addEventListener('htmx:responseError', this.handleError);
    document.body.addEventListener('htmx:sendError', this.handleError);

    // Optional: Clear error state after swap
    document.body.addEventListener('htmx:afterSwap', this.handleAfterSwap);
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    document.body.removeEventListener(
      'htmx:beforeRequest',
      this.handleBeforeRequest,
    );
    document.body.removeEventListener(
      'htmx:afterRequest',
      this.handleAfterRequest,
    );
    document.body.removeEventListener('htmx:responseError', this.handleError);
    document.body.removeEventListener('htmx:sendError', this.handleError);
    document.body.removeEventListener('htmx:afterSwap', this.handleAfterSwap);
  }

  private handleBeforeRequest = () => {
    this.requestCount++;
    this.visible = true;
    this.error = false;
  };

  private handleAfterRequest = (event: Event) => {
    const customEvent = event as CustomEvent;
    this.requestCount = Math.max(0, this.requestCount - 1);

    // Only hide if no more requests are pending
    if (this.requestCount === 0) {
      // Check if this specific request was successful
      if (customEvent.detail?.successful !== false) {
        this.visible = false;
        this.error = false;
      }
    }
  };

  private handleError = () => {
    this.requestCount = Math.max(0, this.requestCount - 1);
    this.error = true;
    this.visible = true;

    // Auto-hide error state after a delay
    setTimeout(() => {
      if (this.requestCount === 0) {
        this.visible = false;
        this.error = false;
      }
    }, 3000);
  };

  private handleAfterSwap = () => {
    // If we're showing an error but content swapped successfully, clear the error
    if (this.error && this.requestCount === 0) {
      this.visible = false;
      this.error = false;
    }
  };

  render() {
    const classes = [
      'loading-bar',
      this.visible ? 'visible' : '',
      this.error ? 'error' : 'normal',
    ]
      .filter(Boolean)
      .join(' ');

    return html`
      <div
        class=${classes}
        role="progressbar"
        aria-live="polite"
        aria-busy=${this.visible}
      >
        <div class="progress-inner"></div>
      </div>
    `;
  }
}
