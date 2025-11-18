import type { ITheme } from 'survey-core';
import { LayeredLightPanelless } from 'survey-core/themes';

const CustomSandwichTheme: ITheme = {
  themeName: 'sandwich-custom',
  colorPalette: 'light',
  isPanelless: true,
  cssVariables: {
    ...LayeredLightPanelless.cssVariables,
    '--sjs-base-unit': '4px',
    '--sjs-corner-radius': '8px', // This matches rounded-lg, from tailwind
    '--sjs-primary-backcolor': '#0E44AD', // Thrive Blue
  },
};

export default CustomSandwichTheme;
