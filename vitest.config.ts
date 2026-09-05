import { defineConfig } from 'vitest/config';

export default defineConfig({
  // Resolve the path aliases declared in tsconfig.json (incl. `nest g library`).
  resolve: { tsconfigPaths: true },
  test: {
    globals: true,
    root: './',
    include: ['**/*.spec.ts'],
  },
});
