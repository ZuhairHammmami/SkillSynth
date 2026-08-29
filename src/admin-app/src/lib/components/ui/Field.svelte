<!-- Field wrapper: label + control + error, for composed forms. Error is
     announced via role="alert". -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  let { label, error = '', children }: any = $props();
</script>

<div class="field">
  {#if label}<span class="lbl">{label}</span>{/if}
  {@render children()}
  {#if error}<span class="err" role="alert">{error}</span>{/if}
</div>

<style>
  .field { display: block; }
  .lbl { display: block; font-size: 0.82rem; font-weight: 600; color: var(--ink-soft); margin-bottom: 0.3rem; }
  .err { display: block; color: var(--danger); font-size: 0.78rem; margin-top: 0.25rem; }
</style>
