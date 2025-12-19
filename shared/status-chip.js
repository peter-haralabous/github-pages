class StatusChip extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() {
    return ['variant', 'value', 'editable'];
  }

  connectedCallback() {
    this.render();
  }

  attributeChangedCallback(name, oldValue, newValue) {
    if (oldValue !== newValue) {
      this.render();
    }
  }

  getVariantStyles(variant) {
    const variants = {
      'split-view': {
        background: '#d1f4e0',
        color: '#0f5132',
        border: '1px solid #9dd9be',
      },
      'tab-view': {
        background: '#cfe2ff',
        color: '#084298',
        border: '1px solid #9ec5fe',
      },
      'single-view': {
        background: '#f8d7da',
        color: '#842029',
        border: '1px solid #f1aeb5',
      },
      active: {
        background: '#d1f4e0',
        color: '#0f5132',
        border: '1px solid #9dd9be',
      },
      archived: {
        background: '#e9ecef',
        color: '#495057',
        border: '1px solid #ced4da',
      },
      disabled: {
        background: '#f8d7da',
        color: '#842029',
        border: '1px solid #f1aeb5',
      },
      'not-started': {
        background: '#ffffff',
        color: '#6c757d',
        border: '1px solid #dee2e6',
      },
      'in-progress': {
        background: '#fff3cd',
        color: '#664d03',
        border: '1px solid #ffe69c',
      },
      completed: {
        background: '#d1f4e0',
        color: '#0f5132',
        border: '1px solid #9dd9be',
      },
      neutral: {
        background: '#ffffff',
        color: '#6c757d',
        border: '1px solid #dee2e6',
      },
      info: {
        background: '#cfe2ff',
        color: '#084298',
        border: '1px solid #9ec5fe',
      },
      sent: {
        background: '#ffffff',
        color: '#6c757d',
        border: '1px solid #dee2e6',
      },
      ready: {
        background: '#d1f4e0',
        color: '#0f5132',
        border: '1px solid #9dd9be',
      },
      empty: {
        background: '#ffffff',
        color: '#6c757d',
        border: '1px solid #dee2e6',
      },
    };
    return variants[variant] || variants['active'];
  }

  handleChange(e) {
    const newValue = e.target.value;
    const newVariant = this.getVariantFromValue(newValue);
    this.setAttribute('variant', newVariant);
    this.setAttribute('value', newValue);

    // Dispatch custom event for parent components to listen
    this.dispatchEvent(
      new CustomEvent('chip-change', {
        detail: { value: newValue, variant: newVariant },
        bubbles: true,
        composed: true,
      })
    );
  }

  getVariantFromValue(value) {
    const valueMap = {
      'Not started': 'not-started',
      'In Progress': 'in-progress',
      Done: 'completed',
      Active: 'active',
      Archived: 'archived',
      Disabled: 'disabled',
      Split: 'split-view',
      Tabs: 'tab-view',
      Single: 'single-view',
      Sent: 'sent',
      'In progress': 'in-progress',
      Completed: 'completed',
      'Not ready': 'neutral',
      Ready: 'ready',
      Consult: 'neutral',
      'Follow-up': 'neutral',
      '--': 'empty',
    };
    return valueMap[value] || 'active';
  }

  render() {
    const variant = this.getAttribute('variant') || 'active';
    const value = this.getAttribute('value') || 'Active';
    const editable = this.getAttribute('editable') === 'true';
    const styles = this.getVariantStyles(variant);

    if (editable) {
      // Render dropdown
      let options = [];
      if (
        variant === 'sent' ||
        variant === 'in-progress' ||
        variant === 'completed' ||
        variant === 'empty'
      ) {
        // Intake field options - check this first before generic progress check
        options = [
          { value: '--', variant: 'empty' },
          { value: 'Sent', variant: 'sent' },
          { value: 'In progress', variant: 'in-progress' },
          { value: 'Completed', variant: 'completed' },
        ];
      } else if (variant.includes('started') || variant.includes('progress')) {
        options = [
          { value: 'Not started', variant: 'not-started' },
          { value: 'In Progress', variant: 'in-progress' },
          { value: 'Done', variant: 'completed' },
        ];
      } else if (variant === 'active' || variant === 'archived' || variant === 'disabled') {
        options = [
          { value: 'Active', variant: 'active' },
          { value: 'Disabled', variant: 'disabled' },
        ];
      } else if (variant === 'neutral' || variant === 'ready') {
        // Check if this is Ready for review or Appointment Type based on current value
        if (value === 'Ready' || value === 'Not ready') {
          // Ready for review options
          options = [
            { value: 'Not ready', variant: 'neutral' },
            { value: 'Ready', variant: 'ready' },
          ];
        } else {
          // Appointment Type options
          options = [
            { value: 'Consult', variant: 'neutral' },
            { value: 'Follow-up', variant: 'neutral' },
          ];
        }
      }

      this.shadowRoot.innerHTML = `
        <style>
          * {
            box-sizing: border-box;
          }

          :host {
            display: inline-block;
          }

          .chip-dropdown {
            position: relative;
            display: inline-block;
          }

          select {
            appearance: none;
            background: ${styles.background};
            color: ${styles.color};
            border: ${styles.border};
            padding: 8px 32px 8px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
            line-height: 1;
            cursor: pointer;
            transition: all 0.2s ease;
            font-family: inherit;
            outline: none;
          }

          select:hover {
            filter: brightness(0.95);
          }

          select:focus {
            box-shadow: 0 0 0 3px ${styles.background}80;
          }

          .chip-dropdown::after {
            content: '▼';
            position: absolute;
            right: 12px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 10px;
            color: ${styles.color};
            pointer-events: none;
          }
        </style>
        <div class="chip-dropdown">
          <select>
            ${options
              .map(
                (opt) => `
              <option value="${opt.value}" ${opt.value === value ? 'selected' : ''}>
                ${opt.value}
              </option>
            `
              )
              .join('')}
          </select>
        </div>
      `;

      this.shadowRoot.querySelector('select').addEventListener('change', (e) => {
        this.handleChange(e);
      });
    } else {
      // Render static chip
      this.shadowRoot.innerHTML = `
        <style>
          * {
            box-sizing: border-box;
          }

          :host {
            display: inline-block;
          }

          .chip {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: ${styles.background};
            color: ${styles.color};
            border: 1px solid transparent;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
            line-height: 1;
            white-space: nowrap;
            transition: all 0.2s ease;
          }
        </style>
        <span class="chip">
          ${value}
        </span>
      `;
    }
  }
}

customElements.define('status-chip', StatusChip);
