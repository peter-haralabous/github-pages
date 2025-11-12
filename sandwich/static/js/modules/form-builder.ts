import { SurveyCreator } from 'survey-creator-js';
import { getSurveyLicenseKey } from '../lib/survey-license-keys';
import { slk } from 'survey-core';
import * as SurveyCore from 'survey-core';

const ENVIRONMENT = JSON.parse(
  document.getElementById('environment')?.textContent || '',
);

/**
 * Save the survey JSON to the given URL via POST.
 * https://surveyjs.io/survey-creator/documentation/get-started-html-css-javascript#save-and-load-survey-model-schemas
 *
 * @param url
 * @param json
 * @param saveNo
 * @param callback
 */
function saveSurveyJson(
  url: string | null | undefined,
  json: object,
  saveNo: number,
  callback: (saveNo: number, success: boolean) => void,
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

  const successRedirectUrl = document
    .getElementById('form-builder-container')
    ?.getAttribute('data-success-url')!;

  fetch(url, {
    method: 'POST',
    headers,
    body: JSON.stringify(json),
  })
    .then((response) => {
      if (response.ok) {
        callback(saveNo, true);
        window.location.replace(successRedirectUrl);
      } else {
        callback(saveNo, false);
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

  const creator = new SurveyCreator(creatorOptions);

  // Configure save function with creator.
  const saveFormUrl = document
    .getElementById('form-builder-container')
    ?.getAttribute('data-form-save-url');
  creator.saveSurveyFunc = (
    saveNo: number,
    callback: (saveNo: number, success: boolean) => void,
  ) => {
    saveSurveyJson(saveFormUrl, creator.JSON, saveNo, callback);
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

  // Create an action that opens a file picker and hooks into the above handler
  const fileToSurveyAction = new SurveyCore.Action({
    id: 'file-to-survey',
    title: 'Upload File',
    iconName: 'icon-folder-24x24',
    visible: new SurveyCore.ComputedUpdater(
      () => creator.activeTab === 'designer',
    ),
    action: () => openUploadChooser(),
  });

  // Helper to open the hidden form's file chooser and submit on change.
  function openUploadChooser() {
    const form = document.getElementById(
      'file-upload-form',
    ) as HTMLFormElement | null;
    if (!form) {
      creator.notify('File upload form not found on the page.', 'error');
      return;
    }

    const fileInput = form.querySelector(
      'input[type=file]',
    ) as HTMLInputElement | null;
    if (!fileInput) {
      creator.notify('File upload input not found on the page.', 'error');
      return;
    }

    fileInput.addEventListener('change', () => form.requestSubmit());

    fileInput.click();
  }

  // Add the action to the creator toolbars if available
  if (creator.toolbar && Array.isArray(creator.toolbar.actions)) {
    creator.toolbar.actions.push(fileToSurveyAction);
  }
  if (creator.footerToolbar && Array.isArray(creator.footerToolbar.actions)) {
    creator.footerToolbar.actions.push(fileToSurveyAction);
  }
});
