<!-- Hand-built modal dialog. Overlay + ESC-to-close + click-outside + focus trap. No Radix. -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import Icon from '$lib/icons/Icon.svelte';
  let { open = $bindable(false), title = '', onclose, children, footer }: any = $props();

  let dialogEl = $state<HTMLDivElement>();
  let lastFocused: HTMLElement | null = null;

  function onKey(e: KeyboardEvent) {
    if (!open) return;
    if (e.key === 'Escape') { e.stopPropagation(); onclose?.(); return; }
    if (e.key === 'Tab') trapFocus(e);
  }
  function onOverlay(e: MouseEvent) {
    if (e.target === e.currentTarget) onclose?.();
  }
  function trapFocus(e: KeyboardEvent) {
    const focusables = dialogEl?.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
    if (!focusables || focusables.length === 0) return;
    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }
  function focusFirst() {
    const focusables = dialogEl?.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
    (focusables && focusables[0] ? focusables[0] : dialogEl)?.focus();
  }

  $effect(() => {
    if (open) {
      lastFocused = document.activeElement as HTMLElement;
      queueMicrotask(focusFirst);
    } else if (lastFocused) {
      lastFocused.focus();
      lastFocused = null;
    }
  });
</script>

<svelte:window onkeydown={onKey} />

{#if open}
  <div class="overlay" role="presentation" onclick={onOverlay}>
    <div class="dialog" role="dialog" aria-modal="true" aria-labelledby="dialog-title" tabindex="-1" bind:this={dialogEl}>
      <header class="d-head">
        <h3 id="dialog-title">{title}</h3>
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
    position: fixed; inset: 0; background: rgba(42, 37, 33, 0.5);
    display: flex; align-items: center; justify-content: center; padding: 1rem; z-index: 50;
  }
  .dialog {
    background: var(--card); border: 1px solid var(--line-strong);
    border-radius: var(--radius-lg); max-width: 540px; width: 100%;
    max-height: 90vh; overflow: auto; box-shadow: 0 18px 50px rgba(42, 37, 33, 0.25);
  }
  .dialog:focus { outline: none; }
  .d-head { display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.2rem; border-bottom: 1px solid var(--line); }
  .d-head h3 { margin: 0; font-size: 1.15rem; }
  .x { background: transparent; border: 1px solid var(--line-strong); border-radius: var(--radius); cursor: pointer; color: var(--clay); display: inline-flex; align-items: center; justify-content: center; width: 44px; height: 44px; }
  .x:hover { color: var(--ink); background: var(--paper-2); }
  .d-body { padding: 1.2rem; }
  .d-foot { padding: 1rem 1.2rem; border-top: 1px solid var(--line); display: flex; justify-content: flex-end; gap: 0.6rem; }
</style>
