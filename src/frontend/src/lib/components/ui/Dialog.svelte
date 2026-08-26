<!-- Hand-built modal dialog. Overlay + ESC-to-close + click-outside. No Radix. -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import Icon from '$lib/icons/Icon.svelte';
  let { open = $bindable(false), title = '', onclose, children, footer }: any = $props();

  function onKey(e: KeyboardEvent) {
    if (e.key === 'Escape' && open) onclose?.();
  }
  function onOverlay(e: MouseEvent) {
    if (e.target === e.currentTarget) onclose?.();
  }
</script>

<svelte:window onkeydown={onKey} />

{#if open}
  <div class="overlay" role="presentation" onclick={onOverlay}>
    <div class="dialog" role="dialog" aria-modal="true" aria-label={title}>
      <header class="d-head">
        <h3>{title}</h3>
        <button class="x" onclick={onclose} aria-label="Close"><Icon name="x" size={18} /></button>
      </header>
      <div class="d-body">{@render children()}</div>
      {#if footer}
        <footer class="d-foot">{@render footer()}</footer>
      {/if}
    </div>
  </div>
{/if}

<style>
  .overlay {
    position: fixed; inset: 0; background: rgba(42, 37, 33, 0.45);
    display: flex; align-items: center; justify-content: center; padding: 1rem; z-index: 50;
  }
  .dialog {
    background: var(--paper); border: 1px solid var(--line-strong);
    border-radius: var(--radius-lg); max-width: 540px; width: 100%;
    max-height: 90vh; overflow: auto; box-shadow: 0 10px 40px rgba(42, 37, 33, 0.2);
  }
  .d-head { display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.2rem; border-bottom: 1px dashed var(--line-strong); }
  .d-head h3 { margin: 0; font-size: 1.15rem; }
  .x { background: transparent; border: none; cursor: pointer; color: var(--muted); display: inline-flex; }
  .d-body { padding: 1.2rem; }
  .d-foot { padding: 1rem 1.2rem; border-top: 1px dashed var(--line-strong); display: flex; justify-content: flex-end; gap: 0.6rem; }
</style>
