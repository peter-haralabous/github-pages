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
  const creatorContainer = document.getElementById('form-builder-container');
  if (creatorContainer) {
    creator.render(creatorContainer);
  }
});
