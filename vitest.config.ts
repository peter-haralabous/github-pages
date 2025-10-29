import { defineConfig } from 'vitest/config';

// Simple Vitest config to use jsdom so DOM APIs are available in tests.
export default defineConfig({
  test: {
    environment: 'jsdom',
  },
});
