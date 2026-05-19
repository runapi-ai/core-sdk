import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/index.ts', 'src/polling.ts'],
  format: ['cjs', 'esm'],
  dts: true,
  sourcemap: true,
  clean: true,
  target: 'node18',
});
