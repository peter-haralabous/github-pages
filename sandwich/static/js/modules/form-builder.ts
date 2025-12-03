import { SurveyCreator } from 'survey-creator-js';
import { getSurveyLicenseKey } from '../lib/forms/survey-license-keys';
import { Serializer, slk } from 'survey-core';
import * as SurveyCore from 'survey-core';
import CustomSandwichTheme from '../lib/forms/survey-form-theme';
import { registerCustomComponents } from '../components/forms/custom-components';
import { setupAddressAutocomplete } from '../lib/forms/address-autocomplete';
import '../components/message-alert';
import { setupMedicationsAutocomplete } from '../lib/forms/medications-autocomplete';
import { setupFileUploadInput } from '../lib/forms/file-upload';

const ENVIRONMENT = JSON.parse(
  document.getElementById('datadog_vars')?.textContent || '{}',
)['environment'];

/**
 * Save the survey JSON to the given URL via POST.
 * https://surveyjs.io/survey-creator/documentation/get-started-html-css-javascript#save-and-load-survey-model-schemas
 */
function saveSurveyJson(
  url: string | null | undefined,
  json: object,
  saveNo: number,
  callback: (saveNo: number, success: boolean) => void,
  formId: string | undefined,
) {
  if (!url) {
    console.error('Save URL missing.');
    callback(saveNo, false);
    return;
  }

  let headers: Record<string, string> = {
    'Content-Type': 'application/json;charset=UTF-8',
  };
  const csrfToken = document
    .getElementById('form-builder-container')
    ?.getAttribute('data-csrf-token')
    ?.toString();
  if (csrfToken) {
    headers['X-CSRFToken'] = csrfToken;
  }

  fetch(url, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      schema: json,
      form_id: formId ?? null,
    }),
  })
    .then(async (response) => {
      if (response.ok) {
        callback(saveNo, true);
      } else {
        const errorData = await response.json();
        // Use creator.notify to show the detailed error, then mark as failed
        const creator = (window as any).SurveyCreator;
        if (creator && errorData.detail) {
          creator.notify(errorData.detail, 'error');
          callback(saveNo, true); // Pass true to suppress default error notification
        } else {
          callback(saveNo, false); // Let default error show for generic errors
        }
      }
    })
    .catch((error) => {
      console.error('Error saving survey JSON:', error);
      callback(saveNo, false);
    });
}

document.addEventListener('DOMContentLoaded', () => {
  // Auto-save will generate a version of the form for every change/save made,
  // autoSaveEnabled is intentionally not enabled by default.
  const creatorOptions = {
    collapseOnDrag: true,
    showSaveButton: true,
  };

  const licenseKey = getSurveyLicenseKey(ENVIRONMENT);
  if (licenseKey) slk(licenseKey);

  // Register custom components before initializing the creator.
  registerCustomComponents();

  // Force file inputs to store data as binary by default.
  Serializer.findProperty('file', 'storeDataAsText').defaultValue = false;

  const creator = new SurveyCreator(creatorOptions);
  creator.theme = CustomSandwichTheme;

  const _addressAutocompleteUrl = document
    .getElementById('form-builder-container')
    ?.getAttribute('data-address-url');
  const _medicationsAutocompleteUrl = document
    .getElementById('form-builder-container')
    ?.getAttribute('data-medications-url');
  const _fileUploadUrl = document
    .getElementById('form-builder-container')
    ?.getAttribute('data-file-upload-url');
  const _fileDeleteUrl = document
    .getElementById('form-builder-container')
    ?.getAttribute('data-file-delete-url');
  const _fileFetchUrl = document
    .getElementById('form-builder-container')
    ?.getAttribute('data-file-fetch-url');
  const _csrfToken = document
    .getElementById('form-builder-container')
    ?.getAttribute('data-csrf-token')
    ?.toString();

  creator.onSurveyInstanceSetupHandlers.add((_sender, options) => {
    if (options.area !== 'preview-tab') return;
    setupAddressAutocomplete(options.survey, _addressAutocompleteUrl ?? null);
    setupMedicationsAutocomplete(
      options.survey,
      _medicationsAutocompleteUrl ?? null,
    );
    setupFileUploadInput(options.survey, {
      uploadUrl: _fileUploadUrl ?? null,
      deleteUrl: _fileDeleteUrl ?? null,
      fetchUrl: _fileFetchUrl ?? null,
      csrfToken: _csrfToken ?? null,
    });
  });

  // Register onNotify handler to show notifications as toasts
  creator.onNotify.add((sender, options) => {
    const messagesContainer = document.getElementById('messages');
    if (!messagesContainer || options.type === 'info') {
      sender.notifier.notify(options.message, options.type);
      return;
    }

    const messageAlert = document.createElement('message-alert');
    messageAlert.setAttribute('tags', options.type);
    messageAlert.setAttribute('closeable', '');
    messageAlert.textContent = options.message;

    messagesContainer.appendChild(messageAlert);
  });

  // Configure save function with creator.
  const formId =
    document
      .getElementById('form-builder-container')
      ?.getAttribute('data-form-id') ?? undefined;
  const saveFormUrl = document
    .getElementById('form-builder-container')
    ?.getAttribute('data-form-save-url');
  creator.saveSurveyFunc = (
    saveNo: number,
    callback: (saveNo: number, success: boolean) => void,
  ) => {
    saveSurveyJson(saveFormUrl, creator.JSON, saveNo, callback, formId);
  };

  (window as any).SurveyCreator = creator;
  const creatorContainer = document.getElementById('form-builder-container');
  if (creatorContainer) {
    creator.render(creatorContainer);
  }

  // Watch for updates to a <script id="form_schema" type="application/json"> element
  // If present, update the creator.text whenever its content changes.
  const schemaEl = document.getElementById('form_schema');
  if (schemaEl) {
    const applySchema = () => {
      const raw = (schemaEl.textContent || '').trim();
      if (!raw || raw === '""') return;

      // Only accept valid JSON. If parsing fails, do nothing.
      let parsed;
      try {
        parsed = JSON.parse(raw);
      } catch (e) {
        return;
      }

      creator.text = raw;
      creator.notify('Form designer updated.', 'info');
    };

    // Apply initially if there's content
    applySchema();

    // Observe mutations directly on the script element since HTMX may replace the element's content.
    const mo = new MutationObserver(() => applySchema());
    mo.observe(schemaEl, {
      characterData: true,
      childList: true,
      subtree: true,
    });
  }
});
