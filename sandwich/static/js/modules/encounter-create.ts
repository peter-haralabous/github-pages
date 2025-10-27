/**
 * Patient selection and encounter form functionality
 */

export interface PatientData {
  id: string;
  name: string;
  email: string;
  dob: string;
  phn: string;
}

export class EncounterCreateController {
  private selectedPatientId: string | null = null;

  constructor() {
    this.initialize();
  }

  /**
   * Attach the create patient button click handler (for initial and HTMX updates)
   */
  private attachCreatePatientHandler(): void {
    const createButton = document.querySelector('.patient-create-btn');
    if (createButton) {
      createButton.addEventListener('click', (e) => {
        e.preventDefault();
        const searchInput = document.getElementById(
          'patient-search',
        ) as HTMLInputElement;
        const query = searchInput ? searchInput.value : '';
        // You may want to pass organization id as a data attribute on the button for full decoupling
        const orgId = (createButton as HTMLElement).getAttribute(
          'data-organization-id',
        );
        if (orgId) {
          window.location.href = `/providers/organization/${orgId}/patient/add?maybe_name=${encodeURIComponent(query)}&from_encounter=1`;
        }
      });
    }
  }

  /**
   * Re-attach the create patient button handler after HTMX swaps content
   */
  private attachHTMXAfterSwapHandler(): void {
    document.body.addEventListener('htmx:afterSwap', (evt: any) => {
      if (evt.target && evt.target.id === 'patient-search-results') {
        this.attachCreatePatientHandler();
      }
    });
  }

  private initialize(): void {
    // Add event listener for clear patient button
    const clearButton = document.getElementById('clear-patient-btn');
    if (clearButton) {
      clearButton.addEventListener('click', () => this.clearSelectedPatient());
    }

    // Add event delegation for patient selection from search results
    const searchResults = document.getElementById('patient-search-results');
    if (searchResults) {
      searchResults.addEventListener('click', (e) => {
        const button = (e.target as Element).closest(
          '.patient-select-btn',
        ) as HTMLElement;
        if (button) {
          this.selectPatientFromData(button);
        }
      });
    }

    // Attach create patient button handler (for initial and HTMX updates)
    this.attachCreatePatientHandler();
    this.attachHTMXAfterSwapHandler();

    // If there's already a patient selected (form errors), show the form
    const patientField = document.querySelector(
      'input[name="patient"]',
    ) as HTMLInputElement;
    if (patientField && patientField.value) {
      const formContainer = document.getElementById('encounter-form-container');
      if (formContainer) {
        formContainer.classList.remove('hidden');
      }
    }

    // Auto-select patient if auto-select-patient button exists (for new patient flow)
    const autoSelectBtn = document.querySelector(
      '.auto-select-patient',
    ) as HTMLButtonElement | null;
    if (autoSelectBtn) {
      autoSelectBtn.click();
    }
  }

  public selectPatient(patientData: PatientData): void {
    this.selectedPatientId = patientData.id;

    // Hide search results and show selected patient
    const searchResults = document.getElementById('patient-search-results');
    const searchInput = document.getElementById(
      'patient-search',
    ) as HTMLInputElement;
    const selectedPatientName = document.getElementById(
      'selected-patient-name',
    );
    const selectedPatientDetails = document.getElementById(
      'selected-patient-details',
    );
    const selectedPatient = document.getElementById('selected-patient');

    if (searchResults) {
      searchResults.innerHTML = '';
    }

    if (searchInput) {
      searchInput.value = '';
    }

    if (selectedPatientName) {
      selectedPatientName.textContent = patientData.name;
    }

    if (selectedPatientDetails) {
      selectedPatientDetails.textContent = `DOB: ${patientData.dob || 'None'} • PHN: ${patientData.phn || 'None'}`;
    }

    if (selectedPatient) {
      selectedPatient.classList.remove('hidden');
    }

    // Show the encounter form and set the patient
    const formContainer = document.getElementById('encounter-form-container');
    if (formContainer) {
      formContainer.classList.remove('hidden');
    }

    // Set the hidden patient field
    const patientField = document.querySelector(
      'input[name="patient"]',
    ) as HTMLInputElement;
    if (patientField) {
      patientField.value = patientData.id;
    }
  }

  private selectPatientFromData(element: HTMLElement): void {
    const patientData: PatientData = {
      id: element.dataset.patientId || '',
      name: element.dataset.patientName || '',
      email: element.dataset.patientEmail || '',
      dob: element.dataset.patientDob || '',
      phn: element.dataset.patientPhn || '',
    };

    this.selectPatient(patientData);
  }

  private clearSelectedPatient(): void {
    this.selectedPatientId = null;

    const selectedPatient = document.getElementById('selected-patient');
    const formContainer = document.getElementById('encounter-form-container');
    const searchInput = document.getElementById(
      'patient-search',
    ) as HTMLInputElement;

    if (selectedPatient) {
      selectedPatient.classList.add('hidden');
    }

    if (formContainer) {
      formContainer.classList.add('hidden');
    }

    if (searchInput) {
      searchInput.focus();
    }
  }

  public getSelectedPatientId(): string | null {
    return this.selectedPatientId;
  }
}

// Auto-initialize on pages with encounter create functionality
document.addEventListener('DOMContentLoaded', () => {
  // div in the encounter_create template has the data-encounter-create-page attribute
  const encounterCreatePage = document.querySelector(
    '[data-encounter-create-page]',
  );
  if (encounterCreatePage) {
    new EncounterCreateController();
  }
});
