import { SurveyCreator } from 'survey-creator-js';
import { getSurveyLicenseKey } from '../lib/survey-license-keys';
import { slk } from 'survey-core';

const ENVIRONMENT = JSON.parse(
  document.getElementById('environment')?.textContent || '',
);

document.addEventListener('DOMContentLoaded', () => {
  const creatorOptions = {
    autoSaveEnabled: true,
    collapseOnDrag: true,
  };

  const licenseKey = getSurveyLicenseKey(ENVIRONMENT);
  if (licenseKey) slk(licenseKey);

  const creator = new SurveyCreator(creatorOptions);
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
