class CommandPalette extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.searchQuery = '';
    this.selectedIndex = 0;
    this.items = [];
    this.onSelectCallback = null;
  }

  connectedCallback() {
    this.render();
    this.setupEventListeners();
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        * {
          box-sizing: border-box;
        }

        :host {
          display: none;
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          z-index: 9999;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        }

        :host(.open) {
          display: block;
        }

        .overlay {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.5);
          animation: fadeIn 0.2s ease;
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        .palette {
          position: absolute;
          top: 20%;
          left: 50%;
          transform: translateX(-50%);
          width: 90%;
          max-width: 600px;
          background: white;
          border-radius: 12px;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
          overflow: hidden;
          animation: slideDown 0.2s ease;
          padding: 8px;
        }

        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateX(-50%) translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
          }
        }

        .palette-header {
          padding: 16px 20px;
          border-bottom: 1px solid #e5e7eb;
        }

        .palette-title {
          font-size: 18px;
          font-weight: 600;
          color: #374151;
          margin: 0 0 12px 0;
        }

        .search-input {
          width: 100%;
          padding: 12px 16px;
          border: 1px solid #d1d5db;
          border-radius: 8px;
          font-size: 16px;
          outline: none;
          transition: border-color 0.2s;
        }

        .search-input:focus {
          border-color: #2563eb;
        }

        .palette-content {
          max-height: 400px;
          overflow-y: auto;
        }

        .palette-section {
          padding: 12px 20px 8px;
          font-size: 12px;
          font-weight: 600;
          text-transform: uppercase;
          color: #6b7280;
          letter-spacing: 0.5px;
          border-top: 1px solid #e5e7eb;
        }

        .palette-section:first-child {
          border-top: none;
          padding-top: 8px;
        }

        .palette-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 20px;
          cursor: pointer;
          transition: background 0.15s;
          border-bottom: 1px solid #f3f4f6;
        }

        .palette-item:last-child {
          border-bottom: none;
        }

        .palette-item:hover {
          background: #f9fafb;
        }

        .palette-item.selected {
          background: #2563eb;
          color: white;
        }

        .palette-item.selected .item-subtitle {
          color: rgba(255, 255, 255, 0.8);
        }

        .palette-item.selected .item-icon {
          color: white;
        }

        .item-icon {
          flex-shrink: 0;
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #f3f4f6;
          border-radius: 50%;
          color: #6b7280;
        }

        .palette-item.selected .item-icon {
          background: rgba(255, 255, 255, 0.2);
        }

        .item-icon .material-symbols-outlined {
          font-size: 20px;
        }

        .item-content {
          flex: 1;
          min-width: 0;
        }

        .item-title {
          font-size: 15px;
          font-weight: 500;
          color: #111827;
          margin: 0 0 2px 0;
        }

        .palette-item.selected .item-title {
          color: white;
        }

        .item-subtitle {
          font-size: 13px;
          color: #6b7280;
          margin: 0;
        }

        .item-arrow {
          flex-shrink: 0;
          color: #9ca3af;
          font-size: 20px;
        }

        .palette-item.selected .item-arrow {
          color: white;
        }

        .palette-footer {
          padding: 12px 20px;
          background: #f9fafb;
          border-top: 1px solid #e5e7eb;
          font-size: 13px;
          color: #6b7280;
          text-align: center;
        }

        .empty-state {
          padding: 40px 20px;
          text-align: center;
          color: #6b7280;
        }

        .material-symbols-outlined {
          font-family: 'Material Symbols Outlined';
          font-weight: normal;
          font-style: normal;
          font-size: 24px;
          line-height: 1;
          letter-spacing: normal;
          text-transform: none;
          display: inline-block;
          white-space: nowrap;
          word-wrap: normal;
          direction: ltr;
        }
      </style>

      <div class="overlay"></div>
      <div class="palette">
        <div class="palette-header">
          <h2 class="palette-title" id="palette-title">Command Palette</h2>
          <input
            type="text"
            class="search-input"
            id="search-input"
            placeholder="Search..."
            autocomplete="off"
          />
        </div>
        <div class="palette-content" id="palette-content">
          <div class="empty-state">No results found</div>
        </div>
        <div class="palette-footer">
          ↑/↓ to select | Enter to go | Esc to close
        </div>
      </div>
    `;
  }

  setupEventListeners() {
    const overlay = this.shadowRoot.querySelector('.overlay');
    const searchInput = this.shadowRoot.querySelector('#search-input');

    overlay.addEventListener('click', () => this.close());

    searchInput.addEventListener('input', (e) => {
      this.searchQuery = e.target.value.toLowerCase();
      this.filterItems();
    });

    // Handle keyboard navigation
    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        this.selectedIndex = Math.min(this.selectedIndex + 1, this.filteredItems.length - 1);
        this.updateSelection();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        this.selectedIndex = Math.max(this.selectedIndex - 1, 0);
        this.updateSelection();
      } else if (e.key === 'Enter') {
        e.preventDefault();
        this.selectItem();
      } else if (e.key === 'Escape') {
        e.preventDefault();
        this.close();
      }
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.classList.contains('open')) {
        this.close();
      }
    });
  }

  open(options = {}) {
    const { title = 'Command Palette', items = [], sections = [], onSelect } = options;

    // Support both flat items array and sections array
    if (sections && sections.length > 0) {
      this.sections = sections;
      this.items = sections.flatMap((section) => section.items);
    } else {
      this.sections = items.length > 0 ? [{ title: '', items }] : [];
      this.items = items;
    }

    this.filteredItems = [...this.items];
    this.onSelectCallback = onSelect;
    this.selectedIndex = 0;
    this.searchQuery = '';

    // Update title
    this.shadowRoot.querySelector('#palette-title').textContent = title;

    // Clear search input
    const searchInput = this.shadowRoot.querySelector('#search-input');
    searchInput.value = '';

    // Render items
    this.renderItems();

    // Show palette
    this.classList.add('open');

    // Focus search input
    setTimeout(() => searchInput.focus(), 100);
  }

  close() {
    this.classList.remove('open');
    this.items = [];
    this.filteredItems = [];
    this.selectedIndex = 0;
    this.searchQuery = '';
  }

  filterItems() {
    if (!this.searchQuery) {
      this.filteredItems = [...this.items];
      this.filteredSections = this.sections;
    } else {
      this.filteredItems = this.items.filter((item) => {
        const searchText = `${item.title} ${item.subtitle || ''}`.toLowerCase();
        return searchText.includes(this.searchQuery);
      });

      // When searching, group filtered items into sections
      this.filteredSections = this.sections
        .map((section) => ({
          ...section,
          items: section.items.filter((item) => this.filteredItems.includes(item)),
        }))
        .filter((section) => section.items.length > 0);
    }

    this.selectedIndex = 0;
    this.renderItems();
  }

  renderItems() {
    const content = this.shadowRoot.querySelector('#palette-content');

    if (this.filteredItems.length === 0) {
      content.innerHTML = '<div class="empty-state">No results found</div>';
      return;
    }

    let html = '';
    let itemIndex = 0;
    const sectionsToRender = this.filteredSections || this.sections;

    sectionsToRender.forEach((section) => {
      if (section.items.length === 0) return;

      // Add section header if title exists
      if (section.title) {
        html += `<div class="palette-section">${section.title}</div>`;
      }

      // Add items in this section
      section.items.forEach((item) => {
        const globalIndex = this.filteredItems.indexOf(item);
        html += `
          <div class="palette-item ${
            globalIndex === this.selectedIndex ? 'selected' : ''
          }" data-index="${globalIndex}">
            <div class="item-icon">
              <span class="material-symbols-outlined">${item.icon || 'person'}</span>
            </div>
            <div class="item-content">
              <div class="item-title">${item.title}</div>
              ${item.subtitle ? `<div class="item-subtitle">${item.subtitle}</div>` : ''}
            </div>
            <span class="material-symbols-outlined item-arrow">chevron_right</span>
          </div>
        `;
      });
    });

    content.innerHTML = html;

    // Add click handlers to items
    content.querySelectorAll('.palette-item').forEach((element) => {
      const index = parseInt(element.dataset.index);
      element.addEventListener('click', () => {
        this.selectedIndex = index;
        this.selectItem();
      });
    });
  }

  updateSelection() {
    const items = this.shadowRoot.querySelectorAll('.palette-item');
    items.forEach((item, index) => {
      if (index === this.selectedIndex) {
        item.classList.add('selected');
        item.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      } else {
        item.classList.remove('selected');
      }
    });
  }

  selectItem() {
    if (this.filteredItems.length === 0) return;

    const selectedItem = this.filteredItems[this.selectedIndex];
    if (this.onSelectCallback) {
      this.onSelectCallback(selectedItem);
    }

    // Dispatch custom event
    this.dispatchEvent(
      new CustomEvent('item-selected', {
        detail: { item: selectedItem },
        bubbles: true,
        composed: true,
      })
    );
  }
}

customElements.define('command-palette', CommandPalette);
