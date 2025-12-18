class PatientTimeline extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.timeline = null;
  }

  connectedCallback() {
    this.render();
  }

  disconnectedCallback() {
    if (this.timeline) {
      this.timeline.destroy();
    }
  }

  showModal(item) {
    const modal = this.shadowRoot.querySelector('.timeline-modal');
    const modalTitle = this.shadowRoot.querySelector('.modal-title');
    const modalBody = this.shadowRoot.querySelector('.modal-body');

    // Set modal title
    modalTitle.textContent = item.title || item.content;

    // Build modal content
    let content = '';

    if (item.description) {
      content += `<p class="modal-description">${item.description}</p>`;
    }

    if (item.details) {
      content += '<div class="modal-details">';
      Object.entries(item.details).forEach(([key, value]) => {
        const label = key.replace(/([A-Z])/g, ' $1').replace(/^./, (str) => str.toUpperCase());
        content += `
          <div class="detail-row">
            <span class="detail-label">${label}:</span>
            <span class="detail-value">${value}</span>
          </div>
        `;
      });
      content += '</div>';
    }

    modalBody.innerHTML = content || '<p>No additional details available.</p>';
    modal.classList.add('show');
  }

  closeModal() {
    const modal = this.shadowRoot.querySelector('.timeline-modal');
    modal.classList.remove('show');
  }

  getSampleData() {
    // Get today's date
    const today = new Date();
    const todayStr = today.toISOString().split('T')[0];

    // Timeline data matching patient details pages
    const items = [
      // Encounters
      {
        id: 1,
        content: 'Encounter · ' + todayStr,
        start: todayStr,
        type: 'point',
        className: 'encounter',
        title: 'Annual Wellness Visit',
        description:
          'Routine annual wellness examination including vital signs, physical exam, and health screening discussions.',
        details: {
          provider: 'Dr. Sarah Johnson',
          location: 'Main Clinic',
          chiefComplaint: 'Annual wellness visit',
          diagnosis: 'No acute findings',
        },
      },
      {
        id: 2,
        content: 'Encounter · 2025-11-14',
        start: '2025-11-14',
        type: 'point',
        className: 'encounter',
        title: 'Follow-up Visit',
        description:
          'Follow-up appointment to review recent lab results and medication management.',
        details: {
          provider: 'Dr. Sarah Johnson',
          location: 'Main Clinic',
          chiefComplaint: 'Follow-up on hypertension',
          diagnosis: 'Hypertension, controlled',
        },
      },

      // Conditions (chronic - shown as ranges)
      {
        id: 3,
        content: 'Hypertension',
        start: '2001-06-01',
        end: todayStr,
        type: 'range',
        className: 'condition',
        title: 'Essential Hypertension',
        description:
          'Chronic high blood pressure diagnosed in 2001. Currently managed with medication and lifestyle modifications.',
        details: {
          icd10: 'I10',
          status: 'Active',
          onsetDate: '2001-06-01',
          notes:
            'Patient has been compliant with antihypertensive medications. Blood pressure readings have been well-controlled.',
        },
      },
      {
        id: 4,
        content: 'Low back pain',
        start: '2023-03-15',
        end: todayStr,
        type: 'range',
        className: 'condition',
      },
      {
        id: 5,
        content: 'Fibrocystic breast disease',
        start: '2022-08-10',
        end: todayStr,
        type: 'range',
        className: 'condition',
      },
      {
        id: 6,
        content: 'Dizziness',
        start: '2024-02-20',
        end: todayStr,
        type: 'range',
        className: 'condition',
      },
      {
        id: 7,
        content: 'HTN',
        start: '2020-05-12',
        end: todayStr,
        type: 'range',
        className: 'condition',
      },
      {
        id: 8,
        content: 'Chronic Renal Insufficiency',
        start: '2021-09-05',
        end: todayStr,
        type: 'range',
        className: 'condition',
      },
      {
        id: 9,
        content: 'Knee pain (right)',
        start: '2024-06-18',
        end: todayStr,
        type: 'range',
        className: 'condition',
      },
      {
        id: 10,
        content: 'Memory issues',
        start: '2024-08-22',
        end: todayStr,
        type: 'range',
        className: 'condition',
      },

      // Medications (active - shown as ranges)
      {
        id: 11,
        content: 'Warfarin 5mg',
        start: '2023-01-10',
        end: todayStr,
        type: 'range',
        className: 'medication',
      },
      {
        id: 12,
        content: 'Metformin 500mg',
        start: '2022-11-15',
        end: todayStr,
        type: 'range',
        className: 'medication',
      },
      {
        id: 13,
        content: 'Lisinopril 10mg',
        start: '2023-04-20',
        end: todayStr,
        type: 'range',
        className: 'medication',
      },
      {
        id: 14,
        content: 'Atorvastatin 20mg',
        start: '2023-07-08',
        end: todayStr,
        type: 'range',
        className: 'medication',
      },

      // Allergies (point events - when discovered)
      {
        id: 15,
        content: 'Penicillin Allergy',
        start: '2018-03-12',
        type: 'point',
        className: 'allergy',
      },
      {
        id: 16,
        content: 'Latex Allergy',
        start: '2019-07-25',
        type: 'point',
        className: 'allergy',
      },

      // Immunizations
      {
        id: 17,
        content: 'COVID-19 Vaccine',
        start: '2024-09-22',
        type: 'point',
        className: 'immunization',
      },
      {
        id: 18,
        content: 'Influenza Vaccine',
        start: '2024-09-22',
        type: 'point',
        className: 'immunization',
      },

      // Labs
      {
        id: 19,
        content: 'Metabolic Panel',
        start: '2024-11-15',
        type: 'point',
        className: 'lab',
      },

      // Documents
      {
        id: 20,
        content: 'Labs - 2025-12-01',
        start: '2025-12-01',
        type: 'point',
        className: 'lab',
      },
    ];

    return items;
  }

  hideLoader() {
    const loader = this.shadowRoot.querySelector('.timeline-loader');
    if (loader) {
      loader.style.display = 'none';
    }
  }

  initializeTimeline() {
    const container = this.shadowRoot.getElementById('timeline-container');
    const items = this.getSampleData();

    const options = {
      height: '100%',
      margin: {
        item: {
          horizontal: 10,
          vertical: 10,
        },
      },
      stack: true,
      stackSubgroups: true,
      orientation: 'top',
      showCurrentTime: true,
      zoomMin: 1000 * 60 * 60 * 24 * 30, // 1 month
      zoomMax: 1000 * 60 * 60 * 24 * 365 * 50, // 50 years
      start: '2015-01-01',
      end: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30), // 30 days from now
      tooltip: {
        followMouse: true,
        overflowMethod: 'cap',
      },
    };

    // Initialize vis-timeline
    this.timeline = new vis.Timeline(container, items, options);

    // Hide loader after timeline is ready
    // Use a slight delay to ensure timeline has fully rendered
    setTimeout(() => {
      this.hideLoader();
    }, 300);

    // Add click event listener for timeline items
    this.timeline.on('select', (properties) => {
      if (properties.items.length > 0) {
        const itemId = properties.items[0];
        const item = items.find((i) => i.id === itemId);
        if (item) {
          this.showModal(item);
        }
      }
    });

    // Setup fit button
    const fitButton = this.shadowRoot.querySelector('.fit-button');
    fitButton.addEventListener('click', () => {
      // Find earliest and latest dates manually from items
      let minDate = null;
      let maxDate = null;

      items.forEach((item) => {
        const startDate = new Date(item.start);
        const endDate = item.end ? new Date(item.end) : startDate;

        if (!minDate || startDate < minDate) minDate = startDate;
        if (!maxDate || endDate > maxDate) maxDate = endDate;
      });

      if (!minDate || !maxDate) return;

      // Calculate padding (5% on each side)
      const duration = maxDate - minDate;
      const padding = duration * 0.05;

      // Set window with padding and animation
      this.timeline.setWindow(
        new Date(minDate.getTime() - padding),
        new Date(maxDate.getTime() + padding),
        {
          animation: {
            duration: 500,
            easingFunction: 'easeInOutQuad',
          },
        }
      );
    });
  }

  render() {
    this.shadowRoot.innerHTML = `


      <link rel="stylesheet" href="https://unpkg.com/vis-timeline@7.7.3/styles/vis-timeline-graph2d.min.css" />
      <link rel="stylesheet" href="../shared/timeline.css" />
      <script src="https://unpkg.com/vis-timeline@7.7.3/standalone/umd/vis-timeline-graph2d.min.js"></script>

      <div class="timeline-wrapper">
        <div class="timeline-header">
          <h2>Patient Timeline</h2>
          <p>View all patient health events, encounters, and milestones in chronological order</p>
        </div>

        <div class="timeline-legend">
          <div class="legend-items">
            <div class="legend-item">
              <span class="legend-dot encounter"></span>
              <span>Encounters</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot lab"></span>
              <span>Labs</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot medication"></span>
              <span>Medications</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot immunization"></span>
              <span>Immunizations</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot allergy"></span>
              <span>Allergies</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot condition"></span>
              <span>Conditions</span>
            </div>
            <div class="legend-item">
              <span class="legend-range"></span>
              <span>Range (ongoing)</span>
            </div>
          </div>
          <button class="fit-button">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 7V5a2 2 0 0 1 2-2h2"/>
              <path d="M17 3h2a2 2 0 0 1 2 2v2"/>
              <path d="M21 17v2a2 2 0 0 1-2 2h-2"/>
              <path d="M7 21H5a2 2 0 0 1-2-2v-2"/>
              <rect width="10" height="8" x="7" y="8" rx="1"/>
            </svg>
            <span>Fit to view</span>
          </button>
        </div>

        <div id="timeline-container">
          <div class="timeline-loader">
            <div class="spinner"></div>
            <p>Loading timeline...</p>
          </div>
        </div>

        <!-- Modal -->
        <div class="timeline-modal">
          <div class="modal-content">
            <div class="modal-header">
              <h3 class="modal-title"></h3>
              <button class="modal-close">&times;</button>
            </div>
            <div class="modal-body"></div>
          </div>
        </div>
      </div>
    `;

    // Setup modal close handlers
    const modal = this.shadowRoot.querySelector('.timeline-modal');
    const closeBtn = this.shadowRoot.querySelector('.modal-close');

    closeBtn.addEventListener('click', () => this.closeModal());
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        this.closeModal();
      }
    });

    // Load vis-timeline library if not already loaded
    if (typeof vis === 'undefined') {
      const script = document.createElement('script');
      script.src =
        'https://unpkg.com/vis-timeline@7.7.3/standalone/umd/vis-timeline-graph2d.min.js';
      script.onload = () => {
        this.initializeTimeline();
      };
      document.head.appendChild(script);
    } else {
      // Library already loaded, initialize immediately
      setTimeout(() => this.initializeTimeline(), 0);
    }
  }
}

customElements.define('patient-timeline', PatientTimeline);
