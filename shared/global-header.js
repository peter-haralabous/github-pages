class GlobalHeader extends HTMLElement {
  constructor() {
    super();
    // Attach a shadow DOM
    this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    this.render();
    this.setupEventListeners();

    // Add the body class for proper styling
    if (!document.body.classList.contains('has-global-header')) {
      document.body.classList.add('has-global-header');
    }
  }

  disconnectedCallback() {
    // Clean up when component is removed
    document.body.classList.remove('has-global-header');
  }

  render() {
    const homeUrl = this.getAttribute('home-url') || './index.html';

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
        }

        .global-header {
          background: white;
          border-bottom: 1px solid rgba(11, 18, 32, 0.06);
          position: sticky;
          top: 0;
          z-index: 100;
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
          background: #0f172a;
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
          gap: 12px;
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
          border: 1px solid rgba(11, 18, 32, 0.06);
          border-radius: 12px;
          box-shadow: 0 8px 24px rgba(11, 18, 32, 0.12);
          min-width: 280px;
          opacity: 0;
          visibility: hidden;
          transform: translateY(-8px);
          transition: opacity 0.2s, transform 0.2s, visibility 0.2s;
          z-index: 1000;
        }

        .dropdown-menu.show {
          opacity: 1;
          visibility: visible;
          transform: translateY(0);
        }

        .dropdown-header {
          padding: 16px;
          border-bottom: 1px solid rgba(11, 18, 32, 0.06);
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .dropdown-avatar {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          background: #e9ecef;
          color: #6c757d;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .dropdown-avatar-icon {
          font-size: 42px;
        }

        .dropdown-user-info {
          flex: 1;
        }

        .dropdown-user-name {
          font-size: 16px;
          font-weight: 600;
          color: #0b1220;
          margin: 0 0 4px 0;
        }

        .dropdown-user-email {
          font-size: 13px;
          color: #6c757d;
          margin: 0;
        }

        .dropdown-section-title {
          padding: 12px 16px 8px;
          font-size: 12px;
          font-weight: 600;
          color: #6c757d;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          margin: 0;
        }

        .dropdown-menu-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 16px;
          color: #0b1220;
          text-decoration: none;
          cursor: pointer;
          background: none;
          border: none;
          width: 100%;
          font-size: 14px;
          font-family: 'Inter', sans-serif;
          transition: background 0.2s;
        }

        .dropdown-menu-item:hover {
          background: #f6f6f8;
        }

        .dropdown-menu-item .material-symbols-outlined {
          font-size: 20px;
          color: #6c757d;
        }

        .dropdown-menu-item .chevron {
          margin-left: auto;
          font-size: 16px;
        }

        .dropdown-org-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 16px;
          width: 100%;
          background: none;
          border: none;
          cursor: pointer;
          font-family: 'Inter', sans-serif;
          transition: background 0.2s;
        }

        .dropdown-org-item:hover {
          background: #f6f6f8;
        }

        .dropdown-org-icon {
          font-size: 20px;
          color: #6c757d;
        }

        .dropdown-org-name {
          flex: 1;
          text-align: left;
          font-size: 14px;
          color: #0b1220;
        }

        .dropdown-org-toggle {
          color: #6c757d;
        }

        .dropdown-org-toggle .material-symbols-outlined {
          font-size: 20px;
        }

        .dropdown-logout {
          border-top: 1px solid rgba(11, 18, 32, 0.06);
          color: #dc3545;
        }

        .dropdown-logout .material-symbols-outlined {
          color: #dc3545;
        }

        /* Material Symbols */
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
          -webkit-font-feature-settings: 'liga';
          -webkit-font-smoothing: antialiased;
        }
      </style>

      <header class="global-header">
        <div class="global-header__inner">
          <a href="${homeUrl}" class="brand">
            <span class="logo">HC</span>
            <span class="brand-name">HealthConnect</span>
          </a>
          <div class="search">
            <input type="search" placeholder="Search for a patient..." aria-label="Search" />
          </div>
          <div class="actions">
            <button class="icon-btn" aria-label="Open quick actions" title="Open quick actions">
              <span class="material-symbols-outlined"></span>
            </button>
            <div class="user-avatar-wrapper">
              <div class="user-avatar" id="userAvatarBtn">
                <span class="material-symbols-outlined user-avatar-icon">account_circle</span>
              </div>
              <div class="dropdown-menu" id="userDropdown">
                <div class="dropdown-header">
                  <div class="dropdown-avatar">
                    <span class="material-symbols-outlined dropdown-avatar-icon">account_circle</span>
                  </div>
                  <div class="dropdown-user-info">
                    <h3 class="dropdown-user-name">Dr. Smith</h3>
                    <p class="dropdown-user-email">drsmith@email.com</p>
                  </div>
                </div>

                <a href="./settings/account-settings.html" class="dropdown-menu-item">
                  <span class="material-symbols-outlined">person</span>
                  <span>Account Settings</span>
                  <span class="material-symbols-outlined chevron">chevron_right</span>
                </a>

                <h4 class="dropdown-section-title">Organization</h4>

                <button class="dropdown-org-item">
                  <span class="material-symbols-outlined dropdown-org-icon">apartment</span>
                  <span class="dropdown-org-name">Dr. Smith's Clinic</span>
                  <div class="dropdown-org-toggle">
                    <span class="material-symbols-outlined">unfold_more</span>
                  </div>
                </button>

                <a href="./settings/organization-settings.html" class="dropdown-menu-item">
                  <span class="material-symbols-outlined">settings</span>
                  <span>Organization Settings</span>
                  <span class="material-symbols-outlined chevron">chevron_right</span>
                </a>

                <button class="dropdown-menu-item dropdown-logout">
                  <span class="material-symbols-outlined">logout</span>
                  <span>Log Out</span>
                </button>
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

    avatarBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      dropdown.classList.toggle('show');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', (event) => {
      if (!this.contains(event.target)) {
        dropdown.classList.remove('show');
      }
    });

    // Close dropdown when clicking inside the shadow root but outside the dropdown
    this.shadowRoot.addEventListener('click', (event) => {
      if (!dropdown.contains(event.target) && !avatarBtn.contains(event.target)) {
        dropdown.classList.remove('show');
      }
    });
  }
}

// Define the custom element
customElements.define('global-header', GlobalHeader);
