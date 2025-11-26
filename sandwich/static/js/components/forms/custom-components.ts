import { registerAddressComponent } from './address-autocomplete';

export function registerCustomComponents() {
  // Central place for custom widget registrations so both form builder and form renderer get them.
  registerAddressComponent();
}
