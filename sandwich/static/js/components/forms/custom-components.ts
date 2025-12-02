import { registerAddressComponent } from './address-autocomplete';
import { registerMedicationComponent } from './medication-select';

export function registerCustomComponents() {
  // Central place for custom widget registrations so both form builder and form renderer get them.
  registerAddressComponent();
  registerMedicationComponent();
}
