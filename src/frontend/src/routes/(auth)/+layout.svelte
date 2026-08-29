<!-- Auth layout: split editorial panel (feature blurbs on the side). -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import { t } from '$lib/i18n';
  import Illustration from '$lib/components/Illustration.svelte';
  import Logo from '$lib/components/Logo.svelte';
  import Icon from '$lib/icons/Icon.svelte';
  let { children }: any = $props();
  const features = ['authLayout.feature1', 'authLayout.feature2', 'authLayout.feature3', 'authLayout.feature4'];
</script>

<div class="split">
  <div class="panel-side">
    <Logo />
    <Illustration name="path" width={300} />
    <ul class="features">
      {#each features as f}
        <li>
          <span class="mark"><Icon name="sprout" size={16} /></span>
          <span>{t(f)}</span>
        </li>
      {/each}
    </ul>
  </div>
  <div class="panel-form">
    {@render children()}
  </div>
</div>

<style>
  .split { min-height: 100vh; display: grid; grid-template-columns: 1fr 1fr; }
  .panel-side { background: var(--paper-2); border-inline-end: 1px solid var(--line); padding: 2.5rem; display: flex; flex-direction: column; gap: 1.5rem; justify-content: center; }
  .features { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.7rem; }
  .features li { display: flex; align-items: center; gap: 0.6rem; color: var(--ink-soft); }
  .mark { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 50%; background: var(--ochre-soft); color: var(--ochre-deep); flex-shrink: 0; }
  .panel-form { display: flex; align-items: center; justify-content: center; padding: 2rem; }
  @media (max-width: 800px) { .split { grid-template-columns: 1fr; } .panel-side { display: none; } }
</style>
