// Import status-chip component
import './status-chip.js';

class EncounterSlideout extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
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
          z-index: 1000;
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
          background: rgba(0, 0, 0, 0);
          transition: background 0.3s ease;
        }

        :host(.open) .overlay {
          background: rgba(0, 0, 0, 0.5);
        }

        .slideout {
          position: absolute;
          top: 0;
          right: 0;
          width: 90%;
          max-width: 800px;
          height: 100%;
          background: white;
          box-shadow: -4px 0 24px rgba(0, 0, 0, 0.15);
          transform: translateX(100%);
          transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }

        :host(.open) .slideout {
          transform: translateX(0);
        }

        .header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 20px 24px;
          border-bottom: 1px solid #e9ecef;
          background: white;
          z-index: 10;
        }

        .header-content {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .back-btn {
          background: none;
          border: none;
          cursor: pointer;
          padding: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #6c757d;
          border-radius: 8px;
          transition: background 0.2s;
        }

        .back-btn:hover {
          background: #f8f9fa;
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

        .header-title {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .header-title h2 {
          font-size: 18px;
          font-weight: 600;
          color: #0b1220;
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
          color: #6c757d;
          border-radius: 8px;
          transition: background 0.2s;
        }

        .close-btn:hover {
          background: #f8f9fa;
        }

        .content {
          flex: 1;
          overflow-y: auto;
          padding: 24px;
          background: #f8f9fa;
        }

        .patient-info {
          background: white;
          padding: 20px;
          border-radius: 12px;
          margin-bottom: 20px;
          border: 1px solid #e9ecef;
        }

        .patient-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 16px;
        }

        .patient-name {
          font-size: 24px;
          font-weight: 700;
          color: #0b1220;
          margin: 0;
        }

        .patient-actions {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .btn-view-patient {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 16px;
          background: white;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          color: #0b1220;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
          text-decoration: none;
        }

        .btn-view-patient:hover {
          background: #f8f9fa;
          border-color: #adb5bd;
        }

        .btn-view-patient .material-symbols-outlined {
          font-size: 18px;
        }

        .btn-send-form {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 16px;
          background: #1d7aec;
          border: 1px solid #1d7aec;
          border-radius: 8px;
          color: white;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-send-form:hover {
          background: #1567d3;
          border-color: #1567d3;
        }

        .btn-send-form .material-symbols-outlined {
          font-size: 18px;
        }

        .kebab-menu {
          position: relative;
        }

        .kebab-btn {
          background: none;
          border: none;
          cursor: pointer;
          padding: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #6c757d;
          border-radius: 8px;
          transition: background 0.2s;
        }

        .kebab-btn:hover {
          background: #f8f9fa;
        }

        .kebab-btn .material-symbols-outlined {
          font-size: 20px;
        }

        .kebab-dropdown {
          display: none;
          position: absolute;
          top: 100%;
          right: 0;
          margin-top: 4px;
          background: white;
          border: 1px solid #e9ecef;
          border-radius: 8px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
          min-width: 180px;
          z-index: 100;
        }

        .kebab-dropdown.show {
          display: block;
        }

        .kebab-dropdown button {
          width: 100%;
          padding: 10px 16px;
          background: none;
          border: none;
          text-align: left;
          cursor: pointer;
          font-size: 14px;
          color: #0b1220;
          transition: background 0.2s;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .kebab-dropdown button:hover {
          background: #f8f9fa;
        }

        .kebab-dropdown button:first-child {
          border-radius: 8px 8px 0 0;
        }

        .kebab-dropdown button:last-child {
          border-radius: 0 0 8px 8px;
        }

        .kebab-dropdown button .material-symbols-outlined {
          font-size: 18px;
          color: #6c757d;
        }

        .kebab-dropdown button.archive-item {
          color: #dc3545;
        }

        .kebab-dropdown button.archive-item .material-symbols-outlined {
          color: #dc3545;
        }

        .patient-details {
          display: grid;
          gap: 12px;
        }

        .detail-row {
          display: flex;
          align-items: center;
          gap: 8px;
          color: #6c757d;
          font-size: 14px;
        }

        .detail-row .material-symbols-outlined {
          font-size: 20px;
        }

        .section {
          background: white;
          padding: 20px;
          border-radius: 12px;
          margin-bottom: 16px;
          border: 1px solid #e9ecef;
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .section-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 16px;
        }

        .section-title {
          font-size: 16px;
          font-weight: 600;
          color: #0b1220;
          margin: 0 0 8px;
        }

        .status-badge {
          display: inline-block;
          padding: 6px 12px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 500;
        }

        .status-pending {
          background: #fff3cd;
          color: #664d03;
        }

        .status-active {
          background: #d1f4e0;
          color: #0f5132;
        }

        .status-completed {
          background: #d1f4e0;
          color: #0f5132;
        }

        .status-failed {
          background: #f8d7da;
          color: #842029;
        }

        .status-not-started {
          background: #cfe2ff;
          color: #084298;
        }

        .detail-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 16px;
          margin-bottom: 16px;
        }

        .detail-item {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .detail-label {
          font-size: 13px;
          color: #6c757d;
          margin-bottom: .25rem;
          font-weight: 600;
        }

        .detail-value {
          font-size: 14px;
          font-weight: 500;
          color: #0b1220;
        }

        .tags {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }

        .tag {
          padding: 4px 10px;
          border-radius: 6px;
          font-size: 12px;
          font-weight: 500;
        }

        .tag-green {
          background: #d1f4e0;
          color: #0f5132;
        }

        .tag-gray {
          background: #e9ecef;
          color: #495057;
        }

        .summaries-table {
          border: 1px solid #e9ecef;
          border-radius: 8px;
          overflow: hidden;
        }

        .summaries-table table {
          width: 100%;
          border-collapse: collapse;
        }

        .summaries-table th {
          background: #f8f9fa;
          padding: 12px 16px;
          text-align: left;
          font-size: 13px;
          font-weight: 600;
          color: #495057;
          border-bottom: 1px solid #e9ecef;
        }

        .summaries-table td {
          padding: 12px 16px;
          border-bottom: 1px solid #f8f9fa;
          font-size: 14px;
          color: #0b1220;
        }

        .summaries-table tr:last-child td {
          border-bottom: none;
        }

        .summary-name {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .summary-name .material-symbols-outlined {
          font-size: 18px;
        }

        .btn-resend {
          background: #e9ecef;
          color: #0b1220;
          border: none;
          padding: 8px 16px;
          border-radius: 6px;
          font-size: 13px;
          font-weight: 500;
          cursor: pointer;
          transition: background 0.2s;
        }

        .btn-resend:hover {
          background: #dee2e6;
        }

        .btn-add-note {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 6px 12px;
          background: white;
          border: 1px solid #1d7aec;
          border-radius: 6px;
          color: #1d7aec;
          font-size: 13px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-add-note:hover {
          background: #e7f3ff;
        }

        .btn-add-note .material-symbols-outlined {
          font-size: 16px;
        }

        .notes-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .note-item {
          display: flex;
          gap: 12px;
          padding-bottom: 16px;
          border-bottom: 1px solid #e9ecef;
        }

        .note-item:last-child {
          border-bottom: none;
          padding-bottom: 0;
        }

        .note-avatar {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }

        .note-avatar.blue {
          background: #cfe2ff;
        }

        .note-avatar.purple {
          background: #e7d4ff;
        }

        .note-avatar .material-symbols-outlined {
          font-size: 16px;
          color: #0b1220;
        }

        .note-content {
          flex: 1;
        }

        .note-header {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 4px;
        }

        .note-author {
          font-size: 14px;
          font-weight: 500;
          color: #0b1220;
        }

        .note-badge {
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 11px;
          font-weight: 500;
        }

        .note-badge.private {
          background: #fff3cd;
          color: #664d03;
        }

        .note-badge.public {
          background: #cfe2ff;
          color: #084298;
        }

        .note-text {
          font-size: 14px;
          color: #0b1220;
          margin-bottom: 6px;
          line-height: 1.5;
        }

        .note-time {
          font-size: 12px;
          color: #6c757d;
        }

        .activity-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .activity-item {
          display: flex;
          gap: 12px;
        }

        .activity-icon {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }

        .activity-icon.blue {
          background: #cfe2ff;
        }

        .activity-icon.purple {
          background: #e7d4ff;
        }

        .activity-icon.green {
          background: #d1f4e0;
        }

        .activity-icon .material-symbols-outlined {
          font-size: 16px;
          color: #0b1220;
        }

        .activity-content {
          flex: 1;
        }

        .activity-title {
          font-size: 14px;
          font-weight: 500;
          color: #0b1220;
          margin-bottom: 2px;
        }

        .activity-description {
          font-size: 13px;
          color: #6c757d;
          margin-bottom: 4px;
        }

        .activity-time {
          font-size: 12px;
          color: #6c757d;
        }

        .forms-table {
          border: 1px solid #e9ecef;
          border-radius: 8px;
          overflow: hidden;
        }

        .forms-table table {
          width: 100%;
          border-collapse: collapse;
        }

        .forms-table th {
          background: #f8f9fa;
          padding: 12px 16px;
          text-align: left;
          font-size: 13px;
          font-weight: 600;
          color: #495057;
          border-bottom: 1px solid #e9ecef;
        }

        .forms-table td {
          padding: 12px 16px;
          border-bottom: 1px solid #f8f9fa;
          font-size: 14px;
          color: #0b1220;
        }

        .forms-table tr:last-child td {
          border-bottom: none;
        }

        .forms-table tbody tr {
          cursor: pointer;
        }

        .forms-table tbody tr:hover {
          background: #f8f9fa;
        }

        .form-name {
          display: flex;
          align-items: center;
          gap: 8px;
          color: #1d7aec;
          font-weight: 500;
          cursor: pointer;
        }

        .form-name:hover {
          text-decoration: underline;
        }

        .form-name .material-symbols-outlined {
          font-size: 18px;
        }

        .summary-name a {
          color: #1d7aec;
          text-decoration: none;
        }

        .summary-name a:hover {
          text-decoration: underline;
        }
      </style>

      <div class="overlay"></div>
      <div class="slideout">
        <div class="header">
          <div class="header-content">
            <button class="back-btn" aria-label="Back to encounters list">
              <span class="material-symbols-outlined">arrow_back</span>
            </button>
            <div class="header-title">
              <span class="material-symbols-outlined">description</span>
              <h2>Encounter Details</h2>
            </div>
          </div>
          <button class="close-btn" aria-label="Close">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="content">
          <div id="encounter-content"></div>
        </div>
      </div>
    `;
  }

  setupEventListeners() {
    const overlay = this.shadowRoot.querySelector('.overlay');
    const closeBtn = this.shadowRoot.querySelector('.close-btn');
    const backBtn = this.shadowRoot.querySelector('.back-btn');

    overlay.addEventListener('click', () => this.close());
    closeBtn.addEventListener('click', () => this.close());
    backBtn.addEventListener('click', () => this.close());
  }

  setupKebabMenu() {
    const kebabBtn = this.shadowRoot.querySelector('.kebab-btn');
    const kebabDropdown = this.shadowRoot.querySelector('.kebab-dropdown');

    if (kebabBtn && kebabDropdown) {
      kebabBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        kebabDropdown.classList.toggle('show');
      });

      // Close dropdown when clicking outside
      document.addEventListener('click', () => {
        kebabDropdown.classList.remove('show');
      });
    }
  }

  setupSendFormButton() {
    const sendFormBtn = this.shadowRoot.querySelector('.btn-send-form');
    if (sendFormBtn) {
      sendFormBtn.addEventListener('click', (e) => {
        e.stopPropagation();

        // Dispatch event for parent to handle
        this.dispatchEvent(
          new CustomEvent('send-form', {
            detail: { patientName: this.currentPatientData?.name },
            bubbles: true,
            composed: true,
          })
        );
      });
    }
  }

  open(patientData) {
    this.currentPatientData = patientData;
    this.classList.add('open');
    this.renderContent(patientData);
    this.setupKebabMenu();
    this.setupSendFormButton();
    this.setupFormLinks();
    document.body.style.overflow = 'hidden';
  }

  close() {
    this.classList.remove('open');
    document.body.style.overflow = '';
  }

  renderContent(data) {
    const contentContainer = this.shadowRoot.querySelector('#encounter-content');

    contentContainer.innerHTML = `
      <div class="patient-info">
        <div class="patient-header">
          <h1 class="patient-name">${data.name}</h1>
          <div class="patient-actions">
            <a href="${data.detailsUrl}" class="btn-view-patient">
              <span class="material-symbols-outlined">open_in_new</span>
              <span>View patient</span>
            </a>
            <button class="btn-send-form">
              <span class="material-symbols-outlined">send</span>
              <span>Send Form</span>
            </button>
            <div class="kebab-menu">
              <button class="kebab-btn" aria-label="More actions">
                <span class="material-symbols-outlined">more_vert</span>
              </button>
              <div class="kebab-dropdown">
                <button>
                  <span class="material-symbols-outlined">person</span>
                  <span>View Patient</span>
                </button>
                <button class="archive-item">
                  <span class="material-symbols-outlined">archive</span>
                  <span>Archive Encounter</span>
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="patient-details">
          <div class="detail-row">
            <span class="material-symbols-outlined">calendar_today</span>
            <span>DOB: ${data.dob}</span>
          </div>
          <div class="detail-row">
            <span class="material-symbols-outlined">badge</span>
            <span>PHN: ${data.phn}</span>
          </div>
          <div class="detail-row">
            <span class="material-symbols-outlined">mail</span>
            <span>Contact: ${data.email}</span>
          </div>
        </div>
      </div>

      <div class="section">
        <div class="section-header">
          <h3 class="section-title">Encounter Details</h3>
          <status-chip variant="${
            data.encounterType === 'Active' ? 'active' : 'archived'
          }" value="${data.encounterType}" editable="true"></status-chip>
        </div>
        <div class="detail-grid">
          <div class="detail-item">
            <span class="detail-label">Created</span>
            <span class="detail-value">${data.created}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Updated</span>
            <span class="detail-value">${data.updated}</span>
          </div>

          ${
            data.intake
              ? `
            <div class="detail-item">
              <span class="detail-label">Intake</span>
              <status-chip variant="${this.getIntakeVariant(data.intake)}" value="${
                data.intake
              }" editable="true"></status-chip>
            </div>
          `
              : ''
          }

          ${
            data.readyForReview
              ? `
            <div class="detail-item">
              <span class="detail-label">Ready for review</span>
              <status-chip variant="${this.getReadyVariant(data.readyForReview)}" value="${
                data.readyForReview
              }" editable="true"></status-chip>
            </div>
          `
              : ''
          }
          ${
            data.appointmentDate
              ? `
            <div class="detail-item">
              <span class="detail-label">Appointment Date</span>
              <span class="detail-value">${data.appointmentDate}</span>
            </div>
          `
              : ''
          }
          ${
            data.appointmentType
              ? `
            <div class="detail-item">
              <span class="detail-label">Appointment Type</span>
              <status-chip variant="neutral" value="${data.appointmentType}" editable="true"></status-chip>
            </div>
          `
              : ''
          }

          ${
            data.concept
              ? `
            <div class="detail-item">
              <span class="detail-label">View</span>
              <status-chip variant="${this.getConceptVariant(data.concept)}" value="${
                data.concept
              }"></status-chip>
            </div>
          `
              : ''
          }
        </div>
      </div>

      ${
        data.summaries && data.summaries.length > 0
          ? `
        <div class="section">
          <h3 class="section-title">Summaries</h3>
          <div class="summaries-table">
            <table>
              <thead>
                <tr>
                  <th>Summary Name</th>
                  <th>Type</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                ${data.summaries
                  .map(
                    (summary) => `
                  <tr>
                    <td>
                      <div class="summary-name">
                        <span class="material-symbols-outlined">summarize</span>
                        <a href="#" class="summary-link" data-summary-id="${
                          summary.id || 'summary-intake'
                        }">${summary.name}</a>
                      </div>
                    </td>
                    <td>${summary.type || 'Form Summary'}</td>
                    <td>${summary.date}</td>
                  </tr>
                `
                  )
                  .join('')}
              </tbody>
            </table>
          </div>
        </div>
      `
          : ''
      }

      ${
        data.forms && data.forms.length > 0
          ? `
        <div class="section">
          <h3 class="section-title">Forms</h3>
          <div class="forms-table">
            <table>
              <thead>
                <tr>
                  <th>Form Name</th>
                  <th>Status</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                ${data.forms
                  .map(
                    (form) => `
                  <tr class="form-row" data-form-id="${form.tabId || this.getFormTabId(form.name)}">
                    <td>
                      <div class="form-name">
                        <span class="material-symbols-outlined">description</span>
                        <span>${form.name}</span>
                      </div>
                    </td>
                    <td>
                      <span class="status-badge ${this.getStatusClass(form.status)}">${
                        form.status
                      }</span>
                    </td>
                    <td>${form.date}</td>
                  </tr>
                `
                  )
                  .join('')}
              </tbody>
            </table>
          </div>
        </div>
      `
          : ''
      }

      ${
        data.notes && data.notes.length > 0
          ? `
        <div class="section">
          <div class="section-header">
            <h3 class="section-title">Notes</h3>
            <button class="btn-add-note">
              <span class="material-symbols-outlined">add</span>
              <span>Add Note</span>
            </button>
          </div>
          <div class="notes-list">
            ${data.notes
              .map(
                (note) => `
              <div class="note-item">
                <div class="note-avatar ${note.avatarColor || 'blue'}">
                  <span class="material-symbols-outlined">person</span>
                </div>
                <div class="note-content">
                  <div class="note-header">
                    <span class="note-author">${note.author}</span>
                    <span class="note-badge ${note.visibility.toLowerCase()}">${
                      note.visibility
                    }</span>
                  </div>
                  <p class="note-text">${note.text}</p>
                  <span class="note-time">${note.time}</span>
                </div>
              </div>
            `
              )
              .join('')}
          </div>
        </div>
      `
          : ''
      }

      ${
        data.activity && data.activity.length > 0
          ? `
        <div class="section">
          <h3 class="section-title">Activity</h3>
          <div class="activity-list">
            ${data.activity
              .map(
                (item) => `
              <div class="activity-item">
                <div class="activity-icon ${item.iconColor || 'blue'}">
                  <span class="material-symbols-outlined">${item.icon}</span>
                </div>
                <div class="activity-content">
                  <div class="activity-title">${item.title}</div>
                  <div class="activity-description">${item.description}</div>
                  <div class="activity-time">${item.time}</div>
                </div>
              </div>
            `
              )
              .join('')}
          </div>
        </div>
      `
          : ''
      }
    `;

    // Add event listeners for summary links
    this.setupSummaryLinks();
  }

  setupSummaryLinks() {
    const summaryLinks = this.shadowRoot.querySelectorAll('.summary-link');
    summaryLinks.forEach((link) => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const summaryId = link.getAttribute('data-summary-id');

        // Dispatch custom event that parent page can listen to
        const event = new CustomEvent('open-summary', {
          detail: { summaryId },
          bubbles: true,
          composed: true,
        });
        this.dispatchEvent(event);

        // Close the slideout
        this.close();
      });
    });
  }

  setupFormLinks() {
    const formRows = this.shadowRoot.querySelectorAll('.form-row');

    formRows.forEach((row) => {
      row.addEventListener('click', () => {
        const formId = row.getAttribute('data-form-id');

        // Dispatch event for parent page to handle
        this.dispatchEvent(
          new CustomEvent('open-form', {
            detail: { formId },
            bubbles: true,
            composed: true,
          })
        );
      });
    });
  }

  getFormTabId(formName) {
    // Convert form name to a tab ID format
    // e.g., "Form 'Intake Form'" -> "intake-form"
    // or "Intake Form" -> "intake-form"
    const match = formName.match(/["']([^"']+)["']/);
    const name = match ? match[1] : formName;
    return name
      .toLowerCase()
      .replace(/\s+/g, '-')
      .replace(/[^a-z0-9-]/g, '');
  }

  getStatusClass(status) {
    const statusLower = status.toLowerCase().replace(/\s+/g, '-');
    if (statusLower.includes('not-started') || statusLower.includes('not started'))
      return 'status-not-started';
    if (statusLower.includes('in-progress') || statusLower.includes('in progress'))
      return 'status-in-progress';
    if (statusLower.includes('done') || statusLower.includes('completed'))
      return 'status-completed';
    if (statusLower.includes('pending')) return 'status-pending';
    if (statusLower.includes('failed')) return 'status-failed';
    return 'status-in-progress';
  }

  getEncounterStatusClass(status) {
    const statusLower = status.toLowerCase();
    if (statusLower.includes('active')) return 'status-active';
    if (statusLower.includes('archived')) return 'status-archived';
    return 'status-active';
  }

  getStatusVariant(status) {
    const statusLower = status.toLowerCase().replace(/\s+/g, '-');
    if (statusLower.includes('not-started') || statusLower.includes('not started'))
      return 'not-started';
    if (statusLower.includes('in-progress') || statusLower.includes('in progress'))
      return 'in-progress';
    if (statusLower.includes('done') || statusLower.includes('completed')) return 'completed';
    return 'in-progress';
  }

  getConceptVariant(concept) {
    const conceptLower = concept.toLowerCase();
    if (conceptLower.includes('split')) return 'split-view';
    if (conceptLower.includes('tab')) return 'tab-view';
    if (conceptLower.includes('single')) return 'single-view';
    return 'split-view';
  }

  getIntakeVariant(value) {
    const map = { Sent: 'sent', 'In progress': 'in-progress', Completed: 'completed' };
    return map[value] || 'sent';
  }

  getReadyVariant(value) {
    return value === 'Ready' ? 'ready' : 'neutral';
  }

  getAppointmentTypeVariant(value) {
    return 'neutral';
  }
}

customElements.define('encounter-slideout', EncounterSlideout);
