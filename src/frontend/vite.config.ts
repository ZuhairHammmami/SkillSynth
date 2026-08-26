import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

/** Vite config — student app serves on port 3000 to match `skillsynth run`. */
export default defineConfig({
  plugins: [sveltekit()],
  server: { port: 3000, strictPort: false },
  preview: { port: 3000 }
});
