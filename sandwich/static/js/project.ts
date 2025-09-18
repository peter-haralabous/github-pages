import '../sass/project.scss';
import './components/command-palette';

/* Project specific Javascript goes here. */

try {
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  document.cookie = `timezone=${timezone}; path=/`;
} catch (e) {
  // the user will see UTC dates, oh well.
}
