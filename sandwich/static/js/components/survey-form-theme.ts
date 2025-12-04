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
    // Add visible borders to inputs for better visibility
    '--sjs-border-default': 'rgba(0, 0, 0, 0.16)',
    '--sjs-border-light': 'rgba(0, 0, 0, 0.09)',
    '--sjs-general-backcolor-dim': '#f8fafc', // Tailwind slate-50
    '--sjs-editorpanel-backcolor': '#ffffff',
    '--sjs-questionpanel-backcolor': '#ffffff',
  },
};

export default CustomSandwichTheme;
