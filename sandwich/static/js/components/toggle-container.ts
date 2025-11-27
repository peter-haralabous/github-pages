import { html, LitElement } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { globalStyles } from './styles';

/**
 * Custom element that toggles the 'hidden' class on its children when the 'toggle-children' event is triggered.
 * Renders children in the Light DOM.
 */
@customElement('toggle-container')
export class ToggleContainer extends LitElement {
  // Render children in Light DOM
  createRenderRoot(): HTMLElement {
    return this;
  }

  connectedCallback(): void {
    super.connectedCallback();
    this.addEventListener('toggle-children', this.toggleChildren);
  }

  disconnectedCallback(): void {
    this.removeEventListener('toggle-children', this.toggleChildren);
    super.disconnectedCallback();
  }

  protected toggleChildren = (): void => {
    Array.from(this.children).forEach((child) => {
      if (child instanceof HTMLElement) {
        if (child.classList.contains('hidden')) {
          child.classList.remove('hidden');
        } else {
          child.classList.add('hidden');
        }
      }
    });
  };

  render() {
    return html`<slot></slot>`;
  }
}

/**
 * Collapse toggle button for use inside <toggle-container>.
 */
@customElement('toggle-button')
export class ToggleButton extends LitElement {
  static styles = [globalStyles];

  @property({ type: String, attribute: 'class' }) accessor class_ = 'btn';

  protected handleClick = (): void => {
    this.dispatchEvent(new Event('toggle-children', { bubbles: true }));
  };

  render() {
    return html`
      <button class=${this.class_} @click=${this.handleClick}>
        <slot></slot>
      </button>
    `;
  }
}
