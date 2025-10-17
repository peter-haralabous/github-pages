import { LitElement, html } from 'lit';
import { customElement, property } from 'lit/decorators.js';

@customElement('message-alert')
export class Message extends LitElement {
  @property({ type: String, attribute: 'tags' }) accessor tags = '';

  @property({ type: String, attribute: 'message' }) accessor message = '';

  private _close() {
    this.remove();
  }

  render() {
    return html`
      <div
        class="alert ${this.tags
          ? `alert-${this.tags}`
          : ''} flex items-center justify-between"
      >
        <span>${this.message}</span>
        <button
          type="button"
          class="btn btn-sm btn-ghost"
          @click=${this._close}
          aria-label="Close"
        >
          &times;
        </button>
      </div>
    `;
  }

  override createRenderRoot() {
    // Render directly into the component's light DOM
    return this;
  }
}
