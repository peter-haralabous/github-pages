class SendFormModal extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.currentStep = 1; // 1 = form selection, 2 = encounter selection
    this.selectedForm = null;
    this.selectedEncounter = null;
    this.showEncounterStep = false;
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
          z-index: 10000;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        }

        :host(.open) {
          display: flex;
          align-items: center;
          justify-content: center;
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

        .modal {
          position: relative;
          background: white;
          border-radius: 12px;
          width: 90%;
          max-width: 600px;
          max-height: 80vh;
          min-height: 500px;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
          animation: slideUp 0.3s ease;
          display: flex;
          flex-direction: column;
          overflow: visible;
        }

        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 24px 24px 16px;
          border-bottom: 1px solid #e5e7eb;
        }

        .modal-title {
          font-size: 20px;
          font-weight: 700;
          color: #111827;
          margin: 0;
        }

        .close-btn {
          background: none;
          border: none;
          cursor: pointer;
          padding: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 8px;
          transition: background 0.2s;
        }

        .close-btn:hover {
          background: #f3f4f6;
        }

        .modal-content {
          padding: 24px;
          overflow-y: auto;
          overflow-x: visible;
          flex: 1;
          min-height: 300px;
        }

        .form-group {
          margin-bottom: 24px;
        }

        .form-label {
          display: block;
          font-size: 14px;
          font-weight: 600;
          color: #374151;
          margin-bottom: 8px;
        }

        .form-label .required {
          color: #ef4444;
        }

        .select-wrapper {
          position: relative;
          z-index: 1;
        }

        .select-input {
          width: 100%;
          padding: 12px 40px 12px 16px;
          border: 2px solid #d1d5db;
          border-radius: 8px;
          font-size: 16px;
          color: #111827;
          background: white;
          cursor: pointer;
          transition: all 0.2s;
          appearance: none;
        }

        .select-input:hover {
          border-color: #9ca3af;
        }

        .select-input:focus {
          outline: none;
          border-color: #2563eb;
          box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }

        .select-input.placeholder {
          color: #9ca3af;
        }

        .select-arrow {
          position: absolute;
          right: 12px;
          top: 50%;
          transform: translateY(-50%);
          pointer-events: none;
          color: #6b7280;
        }

        .dropdown {
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          margin-top: 4px;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
          max-height: 280px;
          overflow-y: auto;
          z-index: 100;
          display: none;
        }

        .dropdown.open {
          display: block;
        }

        .dropdown-header {
          padding: 12px 16px;
          font-size: 13px;
          font-weight: 600;
          color: #6b7280;
          background: #f9fafb;
          border-bottom: 1px solid #e5e7eb;
        }

        .dropdown-item {
          padding: 12px 16px;
          cursor: pointer;
          transition: background 0.15s;
          display: flex;
          align-items: center;
          gap: 8px;
          border-bottom: 1px solid #f3f4f6;
        }

        .dropdown-item:last-child {
          border-bottom: none;
        }

        .dropdown-item:hover {
          background: #f9fafb;
        }

        .dropdown-item.selected {
          background: #eff6ff;
          color: #2563eb;
        }

        .dropdown-item .checkmark {
          margin-left: auto;
          color: #2563eb;
          font-size: 18px;
        }

        .modal-footer {
          display: flex;
          gap: 12px;
          padding: 16px 24px;
          border-top: 1px solid #e5e7eb;
          justify-content: flex-end;
        }

        .btn {
          padding: 10px 20px;
          border-radius: 8px;
          font-size: 15px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          border: none;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .btn-secondary {
          background: #f3f4f6;
          color: #374151;
        }

        .btn-secondary:hover:not(:disabled) {
          background: #e5e7eb;
        }

        .btn-primary {
          background: #2563eb;
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
          background: #1d4ed8;
        }

        .material-symbols-outlined {
          font-family: 'Material Symbols Outlined';
          font-weight: normal;
          font-style: normal;
          font-size: 20px;
          line-height: 1;
          letter-spacing: normal;
          text-transform: none;
          display: inline-block;
          white-space: nowrap;
          word-wrap: normal;
          direction: ltr;
        }

        .step-indicator {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 20px;
        }

        .step {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
          color: #9ca3af;
        }

        .step.active {
          color: #2563eb;
          font-weight: 600;
        }

        .step.completed {
          color: #10b981;
        }

        .step-number {
          width: 24px;
          height: 24px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 12px;
          font-weight: 600;
          background: #e5e7eb;
          color: #6b7280;
        }

        .step.active .step-number {
          background: #2563eb;
          color: white;
        }

        .step.completed .step-number {
          background: #10b981;
          color: white;
        }

        .step-divider {
          width: 40px;
          height: 2px;
          background: #e5e7eb;
        }

        .step.completed ~ .step-divider {
          background: #10b981;
        }

        .btn-create-encounter {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 16px;
          background: white;
          color: #2563eb;
          border: 1px solid #2563eb;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-create-encounter:hover {
          background: #eff6ff;
        }

        .btn-create-encounter .material-symbols-outlined {
          font-size: 18px;
        }

        .encounter-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
          max-height: 320px;
          overflow-y: auto;
        }

        .encounter-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 16px;
          border: 2px solid #e5e7eb;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .encounter-item:hover {
          border-color: #9ca3af;
          background: #f9fafb;
        }

        .encounter-item.selected {
          border-color: #2563eb;
          background: #eff6ff;
        }

        .encounter-item-content {
          flex: 1;
        }

        .encounter-item-title {
          font-size: 15px;
          font-weight: 600;
          color: #111827;
          margin-bottom: 4px;
        }

        .encounter-item-subtitle {
          font-size: 13px;
          color: #6b7280;
        }

        .encounter-item .checkmark,
        .encounter-item .checkmark-empty {
          font-size: 24px;
          color: #2563eb;
        }

        .encounter-item .checkmark-empty {
          color: #d1d5db;
        }

        .encounter-item.selected .checkmark {
          color: #2563eb;
        }
      </style>

      <div class="overlay"></div>
      <div class="modal">
        <div class="modal-header">
          <h2 class="modal-title" id="modal-title">Select a form</h2>
          <button class="close-btn" id="close-btn">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="modal-content" id="modal-content">
          <!-- Content will be rendered dynamically -->
        </div>
        <div class="modal-footer" id="modal-footer">
          <!-- Footer buttons will be rendered dynamically -->
        </div>
      </div>
    `;
  }

  setupEventListeners() {
    const overlay = this.shadowRoot.querySelector('.overlay');
    const closeBtn = this.shadowRoot.querySelector('#close-btn');

    overlay.addEventListener('click', () => this.close());
    closeBtn.addEventListener('click', () => this.close());
  }

  open(options = {}) {
    const { showEncounterSelection = false, patientName = '' } = options;

    this.showEncounterStep = showEncounterSelection;
    this.patientName = patientName;
    this.currentStep = 1;
    this.selectedForm = null;
    this.selectedEncounter = null;

    this.renderContent();
    this.classList.add('open');
  }

  close() {
    this.classList.remove('open');
    this.currentStep = 1;
    this.selectedForm = null;
    this.selectedEncounter = null;
  }

  renderContent() {
    const content = this.shadowRoot.querySelector('#modal-content');
    const title = this.shadowRoot.querySelector('#modal-title');
    const footer = this.shadowRoot.querySelector('#modal-footer');

    if (this.currentStep === 1) {
      title.textContent = 'Select a form*';
      content.innerHTML = this.renderFormSelection();
      footer.innerHTML = this.renderFormFooter();
    } else if (this.currentStep === 2) {
      title.textContent = 'Select an encounter*';
      content.innerHTML = this.renderEncounterSelection();
      footer.innerHTML = this.renderEncounterFooter();
    }

    this.attachContentListeners();
  }

  renderFormSelection() {
    const forms = [
      { id: 'intake-form', name: 'Patient Intake Form' },
      { id: 'patient-symptom', name: 'Patient Symptom Form' },
      { id: 'medical-history', name: 'Medical History Form' },
      { id: 'consent-form', name: 'Consent Form' },
    ];

    return `
      ${
        this.showEncounterStep
          ? `
        <div class="step-indicator">
          <div class="step ${this.currentStep === 1 ? 'active' : ''}">
            <div class="step-number">1</div>
            <span>Select Form</span>
          </div>
          <div class="step-divider"></div>
          <div class="step ${this.currentStep === 2 ? 'active' : ''}">
            <div class="step-number">2</div>
            <span>Select Encounter</span>
          </div>
        </div>
      `
          : ''
      }

      <div class="form-group">
        <label class="form-label">Form <span class="required">*</span></label>
        <div class="select-wrapper">
          <div class="select-input ${
            this.selectedForm ? '' : 'placeholder'
          }" id="form-select" tabindex="0">
            ${this.selectedForm ? this.selectedForm.name : 'Please select a form'}
          </div>
          <span class="material-symbols-outlined select-arrow">expand_more</span>
          <div class="dropdown" id="form-dropdown">
            <div class="dropdown-header">Please select a form</div>
            ${forms
              .map(
                (form) => `
              <div class="dropdown-item" data-id="${form.id}" data-name="${form.name}">
                <span>${form.name}</span>
                ${
                  this.selectedForm?.id === form.id
                    ? '<span class="material-symbols-outlined checkmark">check</span>'
                    : ''
                }
              </div>
            `
              )
              .join('')}
          </div>
        </div>
      </div>
    `;
  }

  renderEncounterSelection() {
    const encounters = [
      {
        id: 'enc-1',
        name: 'Encounter • 2025-11-21',
        created: '2025-11-21 12:11',
        updated: '2025-11-21 12:11',
      },
      {
        id: 'enc-2',
        name: 'Encounter • 2025-11-14',
        created: '2025-11-14 09:30',
        updated: '2025-11-14 09:30',
      },
    ];

    return `
      <div class="step-indicator">
        <div class="step completed">
          <div class="step-number">
            <span class="material-symbols-outlined" style="font-size: 14px;">check</span>
          </div>
          <span>Select Form</span>
        </div>
        <div class="step-divider"></div>
        <div class="step active">
          <div class="step-number">2</div>
          <span>Select Encounter</span>
        </div>
      </div>

      <div class="form-group">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <label class="form-label" style="margin: 0;">Select an existing encounter</label>
          <button class="btn-create-encounter" id="create-encounter-btn">
            <span class="material-symbols-outlined">add</span>
            Create new encounter
          </button>
        </div>

        <div class="encounter-list">
          ${encounters
            .map(
              (enc) => `
            <div class="encounter-item ${
              this.selectedEncounter?.id === enc.id ? 'selected' : ''
            }" data-id="${enc.id}" data-name="${enc.name}">
              <div class="encounter-item-content">
                <div class="encounter-item-title">${enc.name}</div>
                <div class="encounter-item-subtitle">Created: ${enc.created} • Updated: ${
                  enc.updated
                }</div>
              </div>
              ${
                this.selectedEncounter?.id === enc.id
                  ? '<span class="material-symbols-outlined checkmark">check_circle</span>'
                  : '<span class="material-symbols-outlined checkmark-empty">radio_button_unchecked</span>'
              }
            </div>
          `
            )
            .join('')}
        </div>
      </div>
    `;
  }

  renderFormFooter() {
    if (this.showEncounterStep) {
      return `
        <button class="btn btn-secondary" id="cancel-btn">Cancel</button>
        <button class="btn btn-primary" id="next-btn" ${!this.selectedForm ? 'disabled' : ''}>
          Next
          <span class="material-symbols-outlined">arrow_forward</span>
        </button>
      `;
    } else {
      return `
        <button class="btn btn-secondary" id="cancel-btn">Cancel</button>
        <button class="btn btn-primary" id="assign-btn" ${!this.selectedForm ? 'disabled' : ''}>
          Assign task
        </button>
      `;
    }
  }

  renderEncounterFooter() {
    return `
      <button class="btn btn-secondary" id="back-btn">
        <span class="material-symbols-outlined">arrow_back</span>
        Back
      </button>
      <button class="btn btn-primary" id="assign-btn" ${!this.selectedEncounter ? 'disabled' : ''}>
        Assign task
      </button>
    `;
  }

  attachContentListeners() {
    const footer = this.shadowRoot.querySelector('#modal-footer');

    // Form selection listeners
    const formSelect = this.shadowRoot.querySelector('#form-select');
    const formDropdown = this.shadowRoot.querySelector('#form-dropdown');

    if (formSelect && formDropdown) {
      formSelect.addEventListener('click', (e) => {
        e.stopPropagation();
        formDropdown.classList.toggle('open');
      });

      formDropdown.querySelectorAll('.dropdown-item').forEach((item) => {
        item.addEventListener('click', () => {
          this.selectedForm = {
            id: item.dataset.id,
            name: item.dataset.name,
          };
          formSelect.textContent = this.selectedForm.name;
          formSelect.classList.remove('placeholder');
          formDropdown.classList.remove('open');
          this.renderContent();
        });
      });

      // Close dropdown when clicking outside
      document.addEventListener('click', () => {
        formDropdown.classList.remove('open');
      });
    }

    // Encounter selection listeners (list items)
    const encounterItems = this.shadowRoot.querySelectorAll('.encounter-item');

    encounterItems.forEach((item) => {
      item.addEventListener('click', () => {
        this.selectedEncounter = {
          id: item.dataset.id,
          name: item.dataset.name,
        };
        this.renderContent();
      });
    });

    // Create new encounter button
    const createEncounterBtn = this.shadowRoot.querySelector('#create-encounter-btn');

    if (createEncounterBtn) {
      createEncounterBtn.addEventListener('click', () => {
        // Dispatch event to parent to handle encounter creation
        this.dispatchEvent(
          new CustomEvent('create-encounter', {
            detail: { patientName: this.patientName },
            bubbles: true,
            composed: true,
          })
        );

        console.log('Create new encounter for:', this.patientName);
        // For now, just close the modal - parent page should handle encounter creation
        this.close();
      });
    }

    // Footer button listeners
    const cancelBtn = footer.querySelector('#cancel-btn');
    const nextBtn = footer.querySelector('#next-btn');
    const backBtn = footer.querySelector('#back-btn');
    const assignBtn = footer.querySelector('#assign-btn');

    if (cancelBtn) {
      cancelBtn.addEventListener('click', () => this.close());
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        if (this.selectedForm) {
          this.currentStep = 2;
          this.renderContent();
        }
      });
    }

    if (backBtn) {
      backBtn.addEventListener('click', () => {
        this.currentStep = 1;
        this.renderContent();
      });
    }

    if (assignBtn) {
      assignBtn.addEventListener('click', () => {
        if (this.selectedForm && (!this.showEncounterStep || this.selectedEncounter)) {
          this.handleAssignTask();
        }
      });
    }
  }

  handleAssignTask() {
    const detail = {
      form: this.selectedForm,
      encounter: this.selectedEncounter,
      patientName: this.patientName,
    };

    // Dispatch custom event
    this.dispatchEvent(
      new CustomEvent('form-assigned', {
        detail,
        bubbles: true,
        composed: true,
      })
    );

    console.log('Form assigned:', detail);
    this.close();
  }
}

customElements.define('send-form-modal', SendFormModal);
