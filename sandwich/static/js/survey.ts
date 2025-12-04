import 'survey-core/survey-core.min.css';
import 'survey-js-ui';

import { SurveyForm } from './components/survey-form';

if (
  typeof customElements !== 'undefined' &&
  !customElements.get('survey-form')
) {
  customElements.define('survey-form', SurveyForm as any);
}
