import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** SvelteKit config — adapter-node so `pnpm build` produces a runnable server; dev uses vite. */
export default {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter()
  }
};
