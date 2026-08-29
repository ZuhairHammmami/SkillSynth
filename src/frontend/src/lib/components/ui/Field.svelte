<!-- Field wrapper: label + control + error, for composed forms.
     Note: pass a `label` directly to Input/Select for proper association; use
     this only as a layout + error container when the control has no label. -->
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
  .lbl { display: block; font-size: 0.85rem; font-weight: 600; color: var(--ink-soft); margin-bottom: 0.35rem; }
  .err { display: block; color: var(--danger); font-size: 0.78rem; margin-top: 0.3rem; }
</style>
