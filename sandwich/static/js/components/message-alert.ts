import { LitElement, html } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { globalStyles } from './styles';

@customElement('message-alert')
export class MessageAlert extends LitElement {
  static styles = [globalStyles];

  @property({ type: String, attribute: 'tags' }) accessor tags = '';
  @property({ type: Boolean, attribute: 'closeable' }) accessor closeable =
    false;

  private _close() {
    this.remove();
  }

  render() {
    return html`
      <div class="alert ${this.tags ? `alert-${this.tags}` : ''}">
        <slot name="icon">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-info-icon lucide-info size-5"
          >
            <circle cx="12" cy="12" r="10" />
            <path d="M12 16v-4" />
            <path d="M12 8h.01" />
          </svg>
        </slot>
        <slot></slot>
        ${this.closeable
          ? html`<button
              type="button"
              class="btn btn-sm btn-ghost -m-2"
              @click=${this._close}
              aria-label="Close"
            >
              &times;
            </button>`
          : null}
      </div>
    `;
  }
}
