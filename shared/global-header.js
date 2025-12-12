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
      accountCircle: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/></svg>`,
      chevronRight: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M10 6 8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/></svg>`,
      person: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>`,
      expandMore: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M16.59 8.59 12 13.17 7.41 8.59 6 10l6 6 6-6z"/></svg>`,
      expandLess: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 8l-6 6 1.41 1.41L12 10.83l4.59 4.58L18 14z"/></svg>`,
      apartment: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M17 11V3H7v4H3v14h8v-4h2v4h8V11h-4zM7 19H5v-2h2v2zm0-4H5v-2h2v2zm0-4H5V9h2v2zm4 4H9v-2h2v2zm0-4H9V9h2v2zm0-4H9V5h2v2zm4 8h-2v-2h2v2zm0-4h-2V9h2v2zm0-4h-2V5h2v2zm4 12h-2v-2h2v2zm0-4h-2v-2h2v2z"/></svg>`,
      settings: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg>`,
      logout: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="m17 7-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/></svg>`,
    };
  }

  render() {
    const homeUrl = this.getAttribute('home-url') || './index.html';
    const basePath = this.getAttribute('base-path') || '.';
    const icons = this.getIcons();

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
          background: #1e40af;
          color: white;
          width: 36px;
          height: 36px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          font-size: 16px;
        }

        .brand-name {
          font-size: 20px;
          font-weight: 700;
          color: #0b1220;
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
          gap: 8px;
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
          width: 32px;
          height: 32px;
        }

        .icon-lg {
          width: 42px;
          height: 42px;
        }
      </style>

      <header class="global-header">
        <div class="global-header__inner">
          <a href="${homeUrl}" class="brand">
            <span class="logo">TC</span>
            <span class="brand-name">Thrive Clinical</span>
          </a>
          <div class="search">
            <input type="search" placeholder="Search for a patient..." aria-label="Search" />
          </div>
          <div class="actions">
            <button class="icon-btn" aria-label="Open quick actions" title="Open quick actions">
              <span class="material-symbols-outlined"></span>
            </button>
            <div class="user-info">
              <p class="user-name">Dr. Smith</p>
              <p class="user-org" id="headerOrgName">Dr. Smith's Clinic</p>
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

                <!-- Organization Card (Provider Only) -->
                <div class="dropdown-card" id="orgCard">
                  <div class="dropdown-org-section">
                    <div class="dropdown-org-selector-wrapper">
                      <button class="dropdown-org-selector" id="orgToggle">
                        <div class="dropdown-org-selector-left">
                          <div class="icon icon-sm">${icons.apartment}</div>
                          <div class="dropdown-org-info">
                            <p class="dropdown-org-label">Organization</p>
                            <p class="dropdown-org-name" id="currentOrgName">Dr. Smith's Clinic</p>
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
                          <span>Dr. Smith's Clinic</span>
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
                <div class="dropdown-card">
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
