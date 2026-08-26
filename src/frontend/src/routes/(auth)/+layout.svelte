<!-- Auth layout: split editorial panel (feature blurbs on the side). -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import { t } from '$lib/i18n';
  import Illustration from '$lib/components/Illustration.svelte';
  import Logo from '$lib/components/Logo.svelte';
  let { children }: any = $props();
  const features = ['authLayout.feature1', 'authLayout.feature2', 'authLayout.feature3', 'authLayout.feature4'];
</script>

<div class="split">
  <div class="panel-side">
    <Logo />
    <Illustration name="path" width={300} />
    <ul class="features">
      {#each features as f}<li>{t(f)}</li>{/each}
    </ul>
  </div>
  <div class="panel-form">
    {@render children()}
  </div>
</div>

<style>
  .split { min-height: 100vh; display: grid; grid-template-columns: 1fr 1fr; }
  .panel-side { background: var(--paper-2); border-inline-end: 1px solid var(--line); padding: 2.5rem; display: flex; flex-direction: column; gap: 1.5rem; justify-content: center; }
  .features { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.6rem; }
  .features li { padding-inline-start: 1.2rem; position: relative; color: var(--ink-soft); }
  .features li::before { content: '❧'; position: absolute; inset-inline-start: 0; color: var(--ochre); }
  .panel-form { display: flex; align-items: center; justify-content: center; padding: 2rem; }
  @media (max-width: 800px) { .split { grid-template-columns: 1fr; } .panel-side { display: none; } }
</style>
