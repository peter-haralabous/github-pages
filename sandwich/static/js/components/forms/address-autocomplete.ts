import { ComponentCollection, SvgRegistry } from 'survey-core';

export function registerAddressComponent() {
  // Check if already registered to avoid errors in test environments
  if (
    ComponentCollection.Instance.getCustomQuestionByName('addressautocomplete')
  ) {
    return;
  }

  // Register custom map pin icon
  const mapPinIcon =
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="var(--sjs-primary-background-500)" class="size-6">\n' +
    '  <path stroke-linecap="round" stroke-linejoin="round" d="M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />\n' +
    '  <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z" />\n' +
    '</svg>\n';
  SvgRegistry.registerIcon('icon-map-pin', mapPinIcon);

  ComponentCollection.Instance.add({
    name: 'addressautocomplete',
    title: 'Address',
    defaultQuestionTitle: 'Enter your address',
    iconName: 'icon-map-pin',
    questionJSON: {
      type: 'dropdown',
      name: 'suggested_addresses',
      choicesLazyLoadEnabled: true,
      resetValueIf: '{option.filter} empty',
    },
  });
}
