import '../css/project.css';
import 'choices.js/public/assets/styles/choices.css';
import './components/chat-form';
import './components/command-palette';
import './components/enum-formset';
import './components/htmx-loading-bar';
import './components/inline-edit-field';
import './components/message-alert';
import './components/sortable-columns';
import './components/toggle-container';
import './copy-summary';
import './print-summary';
import { initializeDatadog } from './lib/datadog';

/* Project specific Javascript goes here. */
const datadog_vars = JSON.parse(
  document.getElementById('datadog_vars')?.textContent || '',
);

initializeDatadog(datadog_vars);

try {
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  document.cookie = `timezone=${timezone}; path=/`;
} catch (e) {
  // the user will see UTC dates, oh well.
}
