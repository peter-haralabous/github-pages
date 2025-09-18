import { LitElement, html, css, type PropertyValues } from 'lit';
import { property, query, state } from 'lit/decorators.js';
import { unsafeHTML } from 'lit/directives/unsafe-html.js';

class CommandPalette extends LitElement {
  // --- STYLES ---
  // Scoped CSS is a first-class citizen in Lit.
  static styles = css`
    :host {
      display: block;
    }
    .hidden {
      display: none !important;
    }
    .palette-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: rgba(0, 0, 0, 0.5);
      display: flex;
      justify-content: center;
      align-items: flex-start;
      padding-top: 15vh;
    }
    .palette {
      background: white;
      width: 600px;
      max-width: 90%;
      border-radius: 8px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
      overflow: hidden;
    }
    .palette-input {
      width: 100%;
      padding: 16px;
      font-size: 1.2em;
      border: none;
      border-bottom: 1px solid #eee;
      outline: none;
    }
    ul {
      list-style: none;
      margin: 0;
      padding: 0;
      max-height: 400px;
      overflow-y: auto;
    }
    /* Style the content rendered by unsafeHTML */
    li a {
      display: block;
      padding: 12px 16px;
      text-decoration: none;
      color: #333;
    }
    li a.selected {
      background-color: #007bff;
      color: white;
    }
  `;

  // --- REACTIVE PROPERTIES ---
  // Use decorators to declare properties. When these change, the component re-renders.
  @property({ type: String, attribute: 'search-url' }) accessor searchUrl = '';
  @state() accessor isOpen = false;
  @state() accessor selectedIndex = -1;
  @state() accessor resultsHTML = '';

  // --- ELEMENT REFERENCES ---
  // Use the @query decorator to get a direct reference to an element in the template.
  @query('.palette-input') accessor _searchInput!: HTMLInputElement;

  // --- PRIVATE FIELDS ---
  debounceTimer: number | undefined;

  // --- LIFECYCLE & EVENT LISTENERS ---
  connectedCallback() {
    super.connectedCallback();
    document.addEventListener('keydown', this._handleGlobalKeydown);
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    document.removeEventListener('keydown', this._handleGlobalKeydown);
  }

  // updated() is a Lit lifecycle method called after the component's DOM has been updated.
  updated(changedProperties: PropertyValues) {
    // If the palette was just opened, focus the input.
    if (changedProperties.has('isOpen') && this.isOpen) {
      this._searchInput.focus();
      this._performSearch(); // Perform initial search
    }
  }

  // --- METHODS ---
  async _performSearch(query = '') {
    const url = `${this.searchUrl}?q=${encodeURIComponent(query)}`;
    try {
      const response = await fetch(url);
      this.resultsHTML = await response.text();
      this.selectedIndex = -1;
    } catch (error) {
      console.error('Error fetching search results:', error);
      this.resultsHTML = '<p>Error loading results.</p>';
    }
  }

  // --- EVENT HANDLERS ---
  _handleGlobalKeydown = (e: KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      this.isOpen = !this.isOpen;
    }
    if (e.key === 'Escape' && this.isOpen) this.isOpen = false;
  };

  _onInput = (e: InputEvent) => {
    const query = (e.target as HTMLInputElement).value;
    // Debounce search
    clearTimeout(this.debounceTimer);
    this.debounceTimer = setTimeout(() => {
      this._performSearch(query);
    }, 200);
  };

  _onKeydown(e: KeyboardEvent) {
    const results = this.shadowRoot!.querySelectorAll('.palette-results ul li');
    if (results.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        this.selectedIndex = (this.selectedIndex + 1) % results.length;
        break;
      case 'ArrowUp':
        e.preventDefault();
        this.selectedIndex =
          (this.selectedIndex - 1 + results.length) % results.length;
        break;
      case 'Enter':
        e.preventDefault();
        const selectedLink = results[this.selectedIndex]?.querySelector('a');
        if (selectedLink) {
          window.location.href = selectedLink.href;
          this.isOpen = false;
        }
        break;
    }
    this._updateSelectedClass();
  }

  // This is the only manual DOM manipulation we need, as the items are raw HTML
  _updateSelectedClass() {
    const items = this.shadowRoot!.querySelectorAll('.palette-results ul li a');
    items.forEach((item, index) => {
      item.classList.toggle('selected', index === this.selectedIndex);
      if (index === this.selectedIndex)
        item.scrollIntoView({ block: 'nearest' });
    });
  }

  // --- RENDER METHOD ---
  // This is the heart of a Lit component. It describes the component's DOM.
  render() {
    return html`
      <div
        class="palette-overlay ${this.isOpen ? '' : 'hidden'}"
        @click=${(e: MouseEvent) => {
          if (e.target === e.currentTarget) this.isOpen = false;
        }}
      >
        <div class="palette">
          <input
            class="palette-input"
            type="text"
            placeholder="Type a command or search..."
            @input=${this._onInput}
            @keydown=${this._onKeydown}
          />
          <div class="palette-results">
            <ul>
              ${unsafeHTML(this.resultsHTML)}
            </ul>
          </div>
        </div>
      </div>
    `;
  }
}

customElements.define('command-palette', CommandPalette);
