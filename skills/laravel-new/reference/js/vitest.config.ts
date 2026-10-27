import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'jsdom',
    include: ['resources/js/**/*.{test,spec}.{js,jsx,ts,tsx}'],
    setupFiles: ['resources/js/vitest.setup.ts'],
  },
});
