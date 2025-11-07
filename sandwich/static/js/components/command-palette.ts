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
    .palette-title {
      padding: 12px 16px;
      font-size: 0.9em;
      font-weight: 600;
      color: #666;
      background: #f8f9fa;
      border-bottom: 1px solid #eee;
    }
    .palette-input {
      width: 100%;
      padding: 16px;
      font-size: 1.2em;
      border: none;
      border-bottom: 1px solid #eee;
      outline: none;
    }
    .palette-footer {
      background: #f8f9fa;
      padding: 8px 16px;
      font-size: 0.95em;
      color: #666;
      border-top: 1px solid #eee;
      text-align: center;
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
    /* Additional styles for rich content */
    li a > div {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
    }
    li a .result-icon-left {
      width: 16px;
      height: 16px;
      color: #666;
      flex-shrink: 0;
    }
    li a .result-content {
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }
    li a .result-title {
      font-weight: 500;
    }
    li a .result-title:not(:last-child) {
      margin-bottom: 4px;
    }
    li a .result-subtitle {
      font-size: 0.875rem;
      color: #666;
      margin-bottom: 2px;
    }
    li a .result-icon {
      width: 16px;
      height: 16px;
      color: #999;
      flex-shrink: 0;
    }
    li a.selected .result-subtitle {
      color: rgba(255, 255, 255, 0.8);
    }
    li a.selected .result-icon,
    li a.selected .result-icon-left {
      color: rgba(255, 255, 255, 0.7);
    }
  `;

  // --- REACTIVE PROPERTIES ---
  // Use decorators to declare properties. When these change, the component re-renders.
  @property({ type: String, attribute: 'search-url' }) accessor searchUrl = '';
  @property({ type: String, attribute: 'context' }) accessor context = '';
  @property({ type: String, attribute: 'title' }) accessor title = '';
  @property({ type: String, attribute: 'placeholder' })
  accessor placeholder = 'Type a command or search...';
  @state() accessor isOpen = false;
  @state() accessor selectedIndex = -1;
  @state() accessor resultsHTML = '';

  // --- ELEMENT REFERENCES ---
  // Use the @query decorator to get a direct reference to an element in the template.
  @query('.palette-input') accessor _searchInput!: HTMLInputElement;

  // --- PRIVATE FIELDS ---
  debounceTimer: number | undefined;
  // Store default values to reset to
  private _defaultSearchUrl = '';
  private _defaultContext = '';
  private _defaultTitle = '';
  private _defaultPlaceholder = 'Type a command or search...';

  // --- LIFECYCLE & EVENT LISTENERS ---
  connectedCallback() {
    super.connectedCallback();
    // Save initial values
    this._defaultSearchUrl = this.searchUrl;
    this._defaultContext = this.context;
    this._defaultTitle = this.title;
    this._defaultPlaceholder = this.placeholder;
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
    // If the palette was just closed, reset to default context
    if (changedProperties.has('isOpen') && !this.isOpen) {
      this.searchUrl = this._defaultSearchUrl;
      this.context = this._defaultContext;
      this.title = this._defaultTitle;
      this.placeholder = this._defaultPlaceholder;
      this._searchInput.value = ''; // Reset search query
      this.resultsHTML = ''; // Clear results
      this.selectedIndex = 0; // Reset selection
    }
    if (
      changedProperties.has('resultsHTML') ||
      changedProperties.has('selectedIndex')
    ) {
      this._updateSelectedClass();
    }
  }

  // --- METHODS ---
  async _performSearch(query = '') {
    const url = new URL(this.searchUrl, window.location.origin);
    url.searchParams.set('q', query);
    if (this.context) {
      url.searchParams.set('context', this.context);
    }
    try {
      const response = await fetch(url.toString());
      this.resultsHTML = await response.text();
      this.selectedIndex = 0;
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
          this._handleLinkClick(selectedLink as HTMLAnchorElement);
        }
        break;
    }
  }

  _handleLinkClick(link: HTMLAnchorElement) {
    // Check if this link has HTMX attributes
    const hxGet = link.getAttribute('hx-get');
    const hxTarget = link.getAttribute('hx-target');
    const hxSwap = link.getAttribute('hx-swap');

    if (hxGet && hxTarget) {
      // Handle HTMX request manually
      const targetEl = document.querySelector(hxTarget);
      if (targetEl) {
        fetch(hxGet)
          .then((response) => response.text())
          .then((html) => {
            // Safe: HTML comes from our Django backend, which escapes all output by default.
            // The hxGet URL is controlled by our templates, not user input.
            if (hxSwap === 'innerHTML') {
              targetEl.innerHTML = html;
            } else {
              targetEl.outerHTML = html;
            }

            (window as any).htmx?.process(targetEl);

            // The manually swapped html cannot execute scripts, so we need to handle modals here
            const modal = targetEl.querySelector('dialog');
            if (modal && typeof modal.showModal === 'function') {
              modal.showModal();
            }

            document.body.dispatchEvent(
              new CustomEvent('htmx:afterSwap', {
                detail: { target: targetEl },
              }),
            );
          })
          .catch((error) => {
            console.error('Error loading content:', error);
          });
      }
      this.isOpen = false;
    } else {
      // Regular navigation
      window.location.href = link.getAttribute('href') || '#';
      this.isOpen = false;
    }
  }

  _onResultClick = (e: MouseEvent) => {
    const target = e.target as HTMLElement;
    const link = target.closest('a') as HTMLAnchorElement;
    if (link) {
      e.preventDefault();
      this._handleLinkClick(link);
    }
  };

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
          ${this.title
            ? html`<div class="palette-title">${this.title}</div>`
            : ''}
          <input
            class="palette-input"
            type="text"
            placeholder="${this.placeholder}"
            @input=${this._onInput}
            @keydown=${this._onKeydown}
          />
          <div class="palette-results">
            <ul @click=${this._onResultClick}>
              ${unsafeHTML(this.resultsHTML)}
            </ul>
          </div>
          <div class="palette-footer">
            <small>
              ↑/↓ to select &nbsp;|&nbsp; Enter to go &nbsp;|&nbsp; Esc to close
            </small>
          </div>
        </div>
      </div>
    `;
  }
}

customElements.define('command-palette', CommandPalette);
