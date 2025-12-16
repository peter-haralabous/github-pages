class GlobalHeader extends HTMLElement {
  constructor() {
    super();
    // Attach a shadow DOM
    this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    this.render();
    this.setupEventListeners();
  }

  getIcons() {
    return {
      accountCircle: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-circle-user-round"><path d="M18 20a6 6 0 0 0-12 0"/><circle cx="12" cy="10" r="4"/><circle cx="12" cy="12" r="10"/></svg>`,
      chevronRight: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chevron-right"><path d="m9 18 6-6-6-6"/></svg>`,
      person: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-user"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`,
      expandMore: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chevron-down"><path d="m6 9 6 6 6-6"/></svg>`,
      expandLess: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chevron-up"><path d="m18 15-6-6-6 6"/></svg>`,
      apartment: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-hospital"><path d="M12 7v4"/><path d="M14 21v-3a2 2 0 0 0-4 0v3"/><path d="M14 9h-4"/><path d="M18 11h2a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-9a2 2 0 0 1 2-2h2"/><path d="M18 21V5a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16"/></svg>`,
      settings: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-settings"><path d="M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915"/><circle cx="12" cy="12" r="3"/></svg>`,
      logout: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-log-out"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg>`,
    };
  }

  render() {
    const homeUrl = this.getAttribute('home-url') || './index.html';
    const basePath = this.getAttribute('base-path') || '.';
    const icons = this.getIcons();
    const isPatientDetailsPage = window.location.pathname.includes('/patient-details/');

    this.shadowRoot.innerHTML = `
      <style>
        * {
          box-sizing: border-box;
        }

        :host {
          display: block;
        }

        .global-header {
          background: white;
          border-bottom: 1px solid rgba(11, 18, 32, 0.06);
          width: 100%;
        }

        .global-header__inner {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 12px 24px;
          max-width: 100%;
          margin: 0 auto;
        }

        .brand {
          display: flex;
          align-items: center;
          gap: 12px;
          text-decoration: none;
          color: inherit;
        }

        .logo {
          width: 36px;
          height: 36px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          font-size: 16px;
        }
          .logo svg {
          width: 100%;
          height: auto;
          }
        .brand-name {
          font-size: 20px;
          font-weight: 700;
          color: #0b1220;
        }

        .back-button {
          display: flex;
          align-items: center;
          gap: 8px;
          text-decoration: none;
          color: #0b1220;
          padding: 8px 12px;
          border-radius: 8px;
          transition: background 0.2s;
        }

        .back-button:hover {
          background: #f3f4f6;
        }

        .back-button-icon {
          width: 26px;
          height: 26px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .back-button-text {
          font-size: 16px;
          font-weight: 600;
        }

        .search {
          flex: 1;
          max-width: 500px;
          margin: 0 24px;
        }

        .search input {
          width: 100%;
          padding: 10px 16px;
          border: 1px solid rgba(11, 18, 32, 0.1);
          border-radius: 8px;
          font-size: 14px;
          font-family: 'Inter', sans-serif;
        }

        .search input:focus {
          outline: none;
          border-color: #1d7aec;
        }

        .actions {
          display: flex;
          align-items: center;
          gap: 16px;
        }

        .user-info {
          display: flex;
          flex-direction: column;
          align-items: flex-end;
          gap: 2px;
        }

        .user-name {
          font-size: 14px;
          font-weight: 600;
          color: #0b1220;
          margin: 0;
        }

        .user-org {
          font-size: 12px;
          color: #6b7280;
          margin: 0;
        }

        .icon-btn {
          background: none;
          border: none;
          cursor: pointer;
          padding: 8px;
          border-radius: 6px;
          color: #6c757d;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .icon-btn:hover {
          background: #f6f6f8;
        }

        .user-avatar-wrapper {
          position: relative;
        }

        .user-avatar {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          background: #e9ecef;
          color: #6c757d;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: background 0.2s;
        }

        .user-avatar:hover {
          background: #dee2e6;
        }

        .user-avatar-icon {
          font-size: 32px;
        }

        .dropdown-menu {
          position: absolute;
          top: calc(100% + 8px);
          right: 0;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 16px;
          box-shadow: 0 8px 24px rgba(11, 18, 32, 0.16);
          width: 420px;
          opacity: 0;
          visibility: hidden;
          transform: translateY(-8px);
          transition: opacity 0.2s, transform 0.2s, visibility 0.2s;
          z-index: 1000;
          padding: 16px;
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .dropdown-menu.show {
          opacity: 1;
          visibility: visible;
          transform: translateY(0);
        }

        .dropdown-card {
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 12px;
          overflow: visible;
        }

        .dropdown-user-section {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px;
          cursor: pointer;
          transition: background 0.2s;
          text-decoration: none;
          color: inherit;
          width: 100%;
          border: none;
          background: none;
          font-family: 'Inter', sans-serif;
          text-align: left;
          border-radius: 12px;
        }

        .dropdown-user-section:hover {
          background: #f9fafb;
        }

        .dropdown-avatar {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          background: #d1d5db;
          color: #6b7280;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }

        .dropdown-avatar-icon {
          font-size: 32px;
        }

        .dropdown-user-info {
          flex: 1;
          min-width: 0;
        }

        .dropdown-user-name {
          font-size: 16px;
          font-weight: 600;
          color: #0b1220;
          margin: 0 0 4px 0;
        }

        .dropdown-user-email {
          font-size: 14px;
          color: #6b7280;
          margin: 0;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .dropdown-chevron {
          color: #9ca3af;
          flex-shrink: 0;
        }

        .dropdown-chevron .material-symbols-outlined {
          font-size: 20px;
        }

        .dropdown-manage-btn {
          margin: 0 12px 12px;
          padding: 10px 16px;
          border: 1px solid #2563eb;
          border-radius: 12px;
          background: white;
          color: #2563eb;
          font-size: 14px;
          font-weight: 500;
          font-family: 'Inter', sans-serif;
          cursor: pointer;
          transition: background 0.2s;
          text-align: center;
          text-decoration: none;
          display: block;
        }

        .dropdown-manage-btn:hover {
          background: #f9fafb;
        }

        .dropdown-divider {
          border-top: 1px solid #e5e7eb;
        }

        .dropdown-profile-selector {
          padding: 12px;
        }

        .dropdown-profile-btn {
          width: 100%;
          padding: 10px 12px;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          background: white;
          display: flex;
          align-items: center;
          justify-content: space-between;
          cursor: pointer;
          font-family: 'Inter', sans-serif;
          transition: background 0.2s;
        }

        .dropdown-profile-btn:hover {
          background: #f9fafb;
        }

        .dropdown-profile-btn-left {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .dropdown-profile-btn-left .material-symbols-outlined {
          font-size: 20px;
          color: #6b7280;
        }

        .dropdown-profile-btn-left span:last-child {
          color: #0b1220;
          font-size: 14px;
        }

        .dropdown-toggle-icon {
          width: 28px;
          height: 28px;
          border-radius: 50%;
          background: #f3f4f6;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .dropdown-toggle-icon .material-symbols-outlined {
          font-size: 16px;
          color: #6b7280;
        }

        .dropdown-profile-options {
          display: none;
          margin-top: 8px;
          padding: 12px;
          padding-top: 0;
        }
        .dropdown-profile-options-list {
          border: 1px solid #e5e7eb;
          border-radius: 12px;
        }

        .dropdown-profile-options.show {
          display: block;
        }

        .dropdown-profile-option {
          width: 100%;
          padding: 8px 12px;
          border: none;
          background: none;
          display: flex;
          align-items: center;
          gap: 12px;
          cursor: pointer;
          font-family: 'Inter', sans-serif;
          transition: background 0.2s;
          text-align: left;
          border-radius: 8px;
        }

        .dropdown-profile-option:hover {
          background: #f3f4f6;
        }

        .dropdown-profile-option.active {
          background: #eff6ff;
          color: #2563eb;
        }

        .dropdown-profile-icon {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: #e5e7eb;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .dropdown-profile-icon .material-symbols-outlined {
          font-size: 16px;
          color: #6b7280;
        }

        .dropdown-org-section {
          display: flex;
          flex-direction: column;

          gap: .825rem;
        }

        .dropdown-org-selector-wrapper {
          padding: 12px;
          padding-bottom: 0;
        }

        .dropdown-org-selector {
          width: 100%;
          padding: 10px 12px;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          background: white;
          display: flex;
          align-items: center;
          justify-content: space-between;
          cursor: pointer;
          font-family: 'Inter', sans-serif;
          transition: background 0.2s;
        }

        .dropdown-org-selector:hover {
          background: #f9fafb;
        }

        .dropdown-org-selector-left {
          display: flex;
          align-items: center;
          gap: 12px;
          flex: 1;
        }

        .dropdown-org-selector-left .material-symbols-outlined {
          font-size: 20px;
          color: #6b7280;
        }

        .dropdown-org-info {
          text-align: left;
          flex: 1;
        }

        .dropdown-org-label {
          font-size: 11px;
          color: #9ca3af;
          margin: 0 0 2px 0;
          text-transform: uppercase;
          letter-spacing: 0.03em;
          font-weight: 500;
        }

        .dropdown-org-name {
          font-size: 14px;
          color: #0b1220;
          margin: 0;
          font-weight: 600;
        }

        .dropdown-org-options-wrapper {
          padding: 12px;
          padding-top: 0;
        }

        .dropdown-org-options {
          display: none;
          background: white;
          border-radius: 8px;
          border: 1px solid #e5e7eb;
           padding: 12px;
        }

        .dropdown-org-options.show {
          display: block;
          margin-bottom: 12px;
        }

        .dropdown-org-option {
          width: 100%;
          padding: 8px 12px;
          border: none;
          background: white;
          display: flex;
          align-items: center;
          gap: 12px;
          cursor: pointer;
          font-family: 'Inter', sans-serif;
          transition: background 0.2s;
          text-align: left;
          color: #0b1220;
          border-radius: 8px;
        }

        .dropdown-org-option:hover {
          background: #f3f4f6;
        }

        .dropdown-org-option.active {
          background: #dbeafe;
          color: #2563eb;
        }

        .dropdown-org-option-icon {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: #e5e7eb;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .dropdown-org-option-icon .material-symbols-outlined {
          font-size: 16px;
          color: #6b7280;
        }

        .dropdown-settings-btn {
          width: 100%;
          padding: 12px;
          border: none;
          border-radius: 12px;
          background: white;
          display: flex;
          align-items: center;
          gap: 12px;
          cursor: pointer;
          font-family: 'Inter', sans-serif;
          transition: background 0.2s;
          text-decoration: none;
          color: inherit;
        }

        .dropdown-settings-btn:hover {
          background: #f9fafb;
        }

        .dropdown-settings-btn .material-symbols-outlined {
          font-size: 20px;
          color: #6b7280;
        }

        .dropdown-settings-btn span:nth-child(2) {
          flex: 1;
          text-align: left;
          color: #0b1220;
          font-size: 14px;
        }

        .dropdown-settings-btn .chevron {
          color: #9ca3af;
          font-size: 16px;
        }

        .dropdown-logout {
          padding: 10px 12px;
          display: flex;
          align-items: center;
          gap: 12px;
          cursor: pointer;
          border: none;
          background: none;
          width: 100%;
          font-family: 'Inter', sans-serif;
          transition: background 0.2s;
          color: #dc2626;
          font-size: 14px;
          text-align: left;
          border-radius: 12px;
        }

        .dropdown-logout:hover {
          background: #fef2f2;
        }

        .dropdown-logout .material-symbols-outlined {
          font-size: 20px;
          color: #dc2626;
        }

        .hidden {
          display: none;
        }

        /* SVG Icons */
        .icon {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 24px;
          height: 24px;
          flex-shrink: 0;
        }

        .icon svg {
          width: 100%;
          height: 100%;
        }

        .icon-sm {
          width: 20px;
          height: 20px;
        }

        .icon-md {
          width: 24px;
          height: 24px;
        }

        .icon-lg {
          width: 42px;
          height: 42px;
        }
      </style>

      <header class="global-header">
        <div class="global-header__inner">
          ${
            isPatientDetailsPage
              ? `
          <a href="${homeUrl}" class="back-button">
            <span class="back-button-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="m12 19-7-7 7-7"/>
                <path d="M19 12H5"/>
              </svg>
            </span>
            <span class="back-button-text">Patient Encounters</span>
          </a>
          `
              : `
          <a href="${homeUrl}" class="brand">
            <span class="logo">
            <svg id="Layer_2" data-name="Layer 2" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 256 256">
  <defs>
    <style>
      .cls-1 {
        fill: none;
      }

      .cls-2 {
        fill: #003a82;
      }

      .cls-3 {
        clip-path: url(#clippath);
      }
    </style>
    <clipPath id="clippath">
      <rect class="cls-1" width="256" height="256"/>
    </clipPath>
  </defs>
  <g class="cls-3">
    <g>
      <path class="cls-2" d="M205.77,69.63c1.37-16.26,8.28-27.68,8.28-27.68h-22.37c-21.79,0-39.46,17.66-39.46,39.46v22.37h22.36c19.68,0,29.81-17.88,31.18-34.14"/>
      <path class="cls-2" d="M161.57,27.69c1.38-16.27,8.28-27.69,8.28-27.69h-22.37c-21.79,0-39.46,17.67-39.46,39.46v22.37h22.36c19.67,0,29.81-17.88,31.18-34.14"/>
      <path class="cls-2" d="M186.37,205.78c16.26,1.37,27.68,8.28,27.68,8.28v-22.36c0-21.79-17.66-39.46-39.46-39.46h-22.37v22.36c0,19.68,17.88,29.81,34.14,31.18"/>
      <path class="cls-2" d="M228.31,161.57c16.26,1.38,27.68,8.28,27.68,8.28v-22.36c0-21.79-17.66-39.46-39.46-39.46h-22.37v22.37c0,19.67,17.88,29.81,34.14,31.18"/>
      <path class="cls-2" d="M50.23,186.37c-1.37,16.26-8.28,27.68-8.28,27.68h22.36c21.79,0,39.46-17.66,39.46-39.46v-22.36h-22.36c-19.68,0-29.81,17.88-31.18,34.14"/>
      <path class="cls-2" d="M94.43,228.31c-1.38,16.26-8.28,27.68-8.28,27.68h22.36c21.79,0,39.46-17.66,39.46-39.46v-22.37h-22.37c-19.67,0-29.81,17.88-31.18,34.14"/>
      <path class="cls-2" d="M69.63,50.23c-16.26-1.37-27.68-8.28-27.68-8.28v22.37c0,21.79,17.66,39.46,39.46,39.46h22.36v-22.36c0-19.68-17.88-29.81-34.14-31.18"/>
      <path class="cls-2" d="M27.69,94.43c-16.27-1.37-27.69-8.27-27.69-8.27v22.37c0,21.78,17.67,39.45,39.46,39.45h22.37v-22.36c0-19.67-17.88-29.81-34.14-31.18"/>
    </g>
  </g>
</svg>
</span>
            <span class="brand-name">Thrive Clinical</span>
          </a>
          `
          }
          <div class="search">
            <input type="search" placeholder="Search for a patient..." aria-label="Search" />
          </div>
          <div class="actions">
            <button class="icon-btn" aria-label="Open quick actions" title="Open quick actions">
              <span class="material-symbols-outlined"></span>
            </button>
            <div class="user-info">
              <p class="user-name">Dr. Smith</p>
              <p class="user-org" id="headerOrgName">Valley Health Clinic</p>
            </div>
            <div class="user-avatar-wrapper">
              <div class="user-avatar" id="userAvatarBtn">
                <div class="icon icon-md">${icons.accountCircle}</div>
              </div>
              <div class="dropdown-menu" id="userDropdown">
                <!-- User Profile Card -->
                <div class="dropdown-card">
                  <a href="${basePath}/settings/account-settings.html" class="dropdown-user-section">
                    <div class="dropdown-avatar">
                      <div class="icon icon-md">${icons.accountCircle}</div>
                    </div>
                    <div class="dropdown-user-info">
                      <h3 class="dropdown-user-name">Dr. Smith</h3>
                      <p class="dropdown-user-email">drsmith@email.com</p>
                    </div>
                    <div class="dropdown-chevron">
                      <div class="icon icon-sm">${icons.chevronRight}</div>
                    </div>
                  </a>

                  <a href="${basePath}/settings/account-settings.html" class="dropdown-manage-btn">
                    Manage account
                  </a>

                  <div class="dropdown-divider"></div>

                  <!-- Profile Type Selector -->
                  <div class="dropdown-profile-selector">
                    <button class="dropdown-profile-btn" id="profileToggle">
                      <div class="dropdown-profile-btn-left">
                        <div class="icon icon-sm">${icons.person}</div>
                        <span id="currentProfileLabel">Provider</span>
                      </div>
                      <div class="dropdown-toggle-icon">
                        <div class="icon" id="profileToggleIcon">${icons.expandMore}</div>
                      </div>
                    </button>
                  </div>

                  <!-- Profile Options -->
                  <div class="dropdown-profile-options" id="profileOptions">
                  <div class="dropdown-profile-options-list">
                    <button class="dropdown-profile-option active" data-profile="provider">
                      <div class="dropdown-profile-icon">
                        <div class="icon">${icons.person}</div>
                      </div>
                      <span>Provider</span>
                    </button>
                    <button class="dropdown-profile-option" data-profile="personal">
                      <div class="dropdown-profile-icon">
                        <div class="icon">${icons.person}</div>
                      </div>
                      <span>Personal</span>
                    </button>
                    </div>
                  </div>
                </div>

                <!-- Organization Card (Provider Only) -->
                <div class="dropdown-card" id="orgCard">
                  <div class="dropdown-org-section">
                    <div class="dropdown-org-selector-wrapper">
                      <button class="dropdown-org-selector" id="orgToggle">
                        <div class="dropdown-org-selector-left">
                          <div class="icon icon-sm">${icons.apartment}</div>
                          <div class="dropdown-org-info">
                            <p class="dropdown-org-label">Organization</p>
                            <p class="dropdown-org-name" id="currentOrgName">Valley Health Clinic</p>
                          </div>
                        </div>
                        <div class="dropdown-toggle-icon">
                          <div class="icon" id="orgToggleIcon">${icons.expandMore}</div>
                        </div>
                      </button>
                    </div>

                    <!-- Organization Options -->
                    <div class="dropdown-org-options-wrapper">
                      <div class="dropdown-org-options" id="orgOptions">
                        <button class="dropdown-org-option active" data-org="clinic1">
                          <div class="dropdown-org-option-icon">
                            <div class="icon">${icons.apartment}</div>
                          </div>
                          <span>Valley Health Clinic</span>
                        </button>
                        <button class="dropdown-org-option" data-org="clinic2">
                          <div class="dropdown-org-option-icon">
                            <div class="icon">${icons.apartment}</div>
                          </div>
                          <span>Downtown Health Center</span>
                        </button>
                      </div>



                                <!-- Organization Settings Card (Provider Only) -->
                <div class="dropdown-card" id="orgSettingsCard">
                  <a href="${basePath}/settings/organization-settings.html" class="dropdown-settings-btn">
                    <div class="icon icon-sm">${icons.settings}</div>
                    <span>Organization Settings</span>
                    <div class="icon chevron">${icons.chevronRight}</div>
                  </a>
                </div>



                    </div>

                  </div>


                </div>



                <!-- Sign Out Card -->
                <div class="dropdown-card" style="margin-top: 8px">
                  <button class="dropdown-logout" id="logoutBtn">
                    <div class="icon icon-sm">${icons.logout}</div>
                    <span>Sign out</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>
    `;
  }

  setupEventListeners() {
    const avatarBtn = this.shadowRoot.getElementById('userAvatarBtn');
    const dropdown = this.shadowRoot.getElementById('userDropdown');
    const profileToggle = this.shadowRoot.getElementById('profileToggle');
    const profileOptions = this.shadowRoot.getElementById('profileOptions');
    const profileToggleIcon = this.shadowRoot.getElementById('profileToggleIcon');
    const currentProfileLabel = this.shadowRoot.getElementById('currentProfileLabel');
    const orgToggle = this.shadowRoot.getElementById('orgToggle');
    const orgOptions = this.shadowRoot.getElementById('orgOptions');
    const orgToggleIcon = this.shadowRoot.getElementById('orgToggleIcon');
    const currentOrgName = this.shadowRoot.getElementById('currentOrgName');
    const headerOrgName = this.shadowRoot.getElementById('headerOrgName');
    const orgCard = this.shadowRoot.getElementById('orgCard');
    const orgSettingsCard = this.shadowRoot.getElementById('orgSettingsCard');
    const profileOptionBtns = this.shadowRoot.querySelectorAll('.dropdown-profile-option');
    const orgOptionBtns = this.shadowRoot.querySelectorAll('.dropdown-org-option');

    // Toggle main dropdown
    avatarBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      dropdown.classList.toggle('show');
      // Close any open selectors
      const icons = this.getIcons();
      profileOptions.classList.remove('show');
      orgOptions.classList.remove('show');
      profileToggleIcon.innerHTML = icons.expandMore;
      orgToggleIcon.innerHTML = icons.expandMore;
    });

    // Toggle profile selector
    profileToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = profileOptions.classList.toggle('show');
      const icons = this.getIcons();
      profileToggleIcon.innerHTML = isOpen ? icons.expandLess : icons.expandMore;
      // Close org selector if open
      orgOptions.classList.remove('show');
      orgToggleIcon.innerHTML = icons.expandMore;
    });

    // Handle profile selection
    profileOptionBtns.forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const profile = btn.dataset.profile;
        const icons = this.getIcons();

        // Update active state
        profileOptionBtns.forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');

        // Update label
        currentProfileLabel.textContent = profile.charAt(0).toUpperCase() + profile.slice(1);

        // Show/hide org card and settings based on profile
        if (profile === 'provider') {
          orgCard.classList.remove('hidden');
          orgSettingsCard.classList.remove('hidden');
        } else {
          orgCard.classList.add('hidden');
          orgSettingsCard.classList.add('hidden');
        }

        // Close selector
        profileOptions.classList.remove('show');
        profileToggleIcon.innerHTML = icons.expandMore;
      });
    });

    // Toggle organization selector
    orgToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = orgOptions.classList.toggle('show');
      const icons = this.getIcons();
      orgToggleIcon.innerHTML = isOpen ? icons.expandLess : icons.expandMore;
      // Close profile selector if open
      profileOptions.classList.remove('show');
      profileToggleIcon.innerHTML = icons.expandMore;
    });

    // Handle organization selection
    orgOptionBtns.forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const orgName = btn.textContent.trim();
        const icons = this.getIcons();

        // Update active state
        orgOptionBtns.forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');

        // Update org name in dropdown and header
        currentOrgName.textContent = orgName;
        headerOrgName.textContent = orgName;

        // Close selector
        orgOptions.classList.remove('show');
        orgToggleIcon.innerHTML = icons.expandMore;
      });
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', (event) => {
      if (!this.contains(event.target)) {
        const icons = this.getIcons();
        dropdown.classList.remove('show');
        profileOptions.classList.remove('show');
        orgOptions.classList.remove('show');
        profileToggleIcon.innerHTML = icons.expandMore;
        orgToggleIcon.innerHTML = icons.expandMore;
      }
    });

    // Close dropdown when clicking inside the shadow root but outside the dropdown
    this.shadowRoot.addEventListener('click', (event) => {
      if (!dropdown.contains(event.target) && !avatarBtn.contains(event.target)) {
        const icons = this.getIcons();
        dropdown.classList.remove('show');
        profileOptions.classList.remove('show');
        orgOptions.classList.remove('show');
        profileToggleIcon.innerHTML = icons.expandMore;
        orgToggleIcon.innerHTML = icons.expandMore;
      }
    });
  }
}

// Define the custom element
customElements.define('global-header', GlobalHeader);
