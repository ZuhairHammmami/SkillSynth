import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

/** Vite config — admin app serves on port 3001 to match `skillsynth run`. */
export default defineConfig({
  plugins: [sveltekit()],
  server: { port: 3001, strictPort: false },
  preview: { port: 3001 }
});
