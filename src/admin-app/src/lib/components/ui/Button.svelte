<!-- Accessible button. Variants use design tokens only; never hard-coded tints.
     Min 44px touch target, visible focus ring, disabled + loading (spinner) states. -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  let {
    variant = 'primary',
    size = 'md',
    type = 'button',
    disabled = false,
    loading = false,
    onclick,
    children,
    ...rest
  }: any = $props();

  const isInactive = $derived(disabled || loading);
</script>

<button
  class="btn {variant} {size}"
  {type}
  disabled={isInactive}
  aria-disabled={isInactive}
  aria-busy={loading}
  {onclick}
  {...rest}
>
  {#if loading}<span class="spinner" aria-hidden="true"></span>{/if}
  {@render children()}
</button>

<style>
  .btn {
    font-family: var(--font-body);
    font-weight: 600;
    border-radius: var(--radius);
    border: 1px solid transparent;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    line-height: 1.2;
    min-height: 44px;
    min-width: 44px;
    padding: 0.6rem 1.1rem;
    transition: background 0.18s ease, border-color 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
  }
  .btn:focus-visible {
    outline: 2px solid var(--ring);
    outline-offset: 2px;
    box-shadow: 0 0 0 3px var(--focus-glow);
  }
  .btn:active:not(:disabled) { transform: translateY(1px); }
  .btn:disabled { opacity: 0.55; cursor: not-allowed; }
  .sm { padding: 0.5rem 0.8rem; font-size: 0.85rem; }
  .md { padding: 0.6rem 1.1rem; font-size: 0.95rem; }
  .lg { padding: 0.8rem 1.5rem; font-size: 1.05rem; }

  .primary { background: var(--accent); color: #fff; border-color: var(--accent-deep); }
  .primary:hover:not(:disabled) { background: var(--accent-deep); }
  .ghost { background: var(--paper); color: var(--ink-soft); border-color: var(--line-strong); }
  .ghost:hover:not(:disabled) { background: var(--paper-2); color: var(--ink); }
  .destructive { background: var(--danger); color: #fff; border-color: var(--danger); }
  .destructive:hover:not(:disabled) { background: color-mix(in srgb, var(--danger) 82%, black); border-color: color-mix(in srgb, var(--danger) 82%, black); }
  .link { background: transparent; color: var(--accent-deep); border-color: transparent; padding-inline: 0.25rem; min-width: 0; }
  .link:hover:not(:disabled) { text-decoration: underline; }

  .spinner {
    width: 1em; height: 1em; border-radius: 50%;
    border: 2px solid currentColor; border-top-color: transparent;
    display: inline-block; animation: spin 0.7s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
</style>
