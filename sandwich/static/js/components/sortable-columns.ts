import { LitElement, html } from 'lit';
import { repeat } from 'lit/directives/repeat.js';
import { customElement, property, state } from 'lit/decorators.js';
import Sortable from 'sortablejs';
import { createIcons, GripVertical } from 'lucide';

interface Column {
  value: string;
  label: string;
  checked: boolean;
}

@customElement('sortable-columns')
export class SortableColumns extends LitElement {
  @property({ type: String, attribute: 'columns-data' }) accessor columnsData =
    '';

  @state() private accessor columns: Column[] = [];

  private sortableInstance: Sortable | null = null;
  private containerEl: HTMLElement | null = null;

  override disconnectedCallback() {
    super.disconnectedCallback();
    if (this.sortableInstance) {
      this.sortableInstance.destroy();
      this.sortableInstance = null;
    }
  }

  override willUpdate(changedProperties: Map<string, unknown>) {
    if (changedProperties.has('columnsData')) {
      if (!this.columnsData) {
        this.columns = [];
      } else {
        try {
          this.columns = JSON.parse(this.columnsData) as Column[];
        } catch (e) {
          console.error('Failed to parse columns data:', e);
          this.columns = [];
        }
      }
    }
  }

  override firstUpdated() {
    this.containerEl = this.querySelector('.sortable-container');
    if (!this.containerEl) return;
    this.sortableInstance = new Sortable(this.containerEl, {
      animation: 150,
      handle: '.drag-handle', // only grip icon acts as handle
      draggable: '.sortable-item',
      onEnd: () => {
        this._updateColumnOrder();
      },
    });
  }

  override updated(changedProperties: Map<string, unknown>) {
    if (changedProperties.has('columns')) {
      this._updateHiddenInputs();
      createIcons({ icons: { GripVertical } });
    }
  }

  private _updateColumnOrder() {
    if (!this.containerEl) return;
    const orderedValues = Array.from(
      this.containerEl.querySelectorAll('.sortable-item'),
    )
      .map((el) => (el as HTMLElement).dataset.columnValue || '')
      .filter(Boolean);
    if (!orderedValues.length) return;
    const lookup = new Map(this.columns.map((c) => [c.value, c]));
    this.columns = orderedValues
      .map((v) => lookup.get(v))
      .filter((c): c is Column => !!c);
  }

  private _handleCheckboxChange(value: string, event: Event) {
    const checked = (event.target as HTMLInputElement).checked;
    this.columns = this.columns.map((col) =>
      col.value === value ? { ...col, checked } : col,
    );
  }

  private _updateHiddenInputs() {
    const form = this.closest('form');
    if (!form) return;
    let container = form.querySelector('#sortable-hidden-inputs');
    if (!container) {
      container = document.createElement('div');
      container.id = 'sortable-hidden-inputs';
      form.insertBefore(container, form.firstChild);
    }
    const fragment = document.createDocumentFragment();
    for (const col of this.columns) {
      if (!col.checked) continue;
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = 'visible_columns';
      input.value = col.value;
      fragment.appendChild(input);
    }
    container.replaceChildren(fragment);
  }

  render() {
    return html`
      <div
        class="sortable-container space-y-2 bg-base-200 p-4 rounded-box"
        role="list"
        aria-label="Reorder columns"
      >
        ${repeat(
          this.columns,
          (c) => c.value,
          (column) => html`
            <div
              class="sortable-item flex items-center gap-2 p-2 bg-base-100 border border-base-300 rounded"
              data-column-value=${column.value}
              role="listitem"
            >
              <i
                data-lucide="grip-vertical"
                class="drag-handle w-4 h-4 opacity-40 cursor-grab"
                aria-label="Drag handle for ${column.label}"
              ></i>
              <input
                type="checkbox"
                data-value=${column.value}
                aria-label="Toggle ${column.label} column visibility"
                .checked=${column.checked}
                @change=${(e: Event) =>
                  this._handleCheckboxChange(column.value, e)}
                class="checkbox checkbox-sm checkbox-primary"
              />
              <span class="flex-1 select-none">${column.label}</span>
            </div>
          `,
        )}
      </div>
    `;
  }

  override createRenderRoot() {
    return this;
  }
}
