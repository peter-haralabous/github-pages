import '../css/project.css';
import './components/command-palette';
import './components/message-alert';
import './modules/encounter-create';
import { initializeDatadog } from './lib/datadog';

/* Project specific Javascript goes here. */

const ENVIRONMENT = JSON.parse(
  document.getElementById('environment')?.textContent || '',
);
const APP_VERSION = JSON.parse(
  document.getElementById('app_version')?.textContent || '',
);

initializeDatadog(ENVIRONMENT, APP_VERSION);

try {
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  document.cookie = `timezone=${timezone}; path=/`;
} catch (e) {
  // the user will see UTC dates, oh well.
}
