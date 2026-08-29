<!-- Warm-Craft button. Hand-styled; no Radix/UI-kit. -->
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
</script>

<button
  class="btn {variant} {size}"
  {type}
  {disabled}
  aria-disabled={disabled || undefined}
  aria-busy={loading || undefined}
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
    transition: background 0.18s ease, border-color 0.18s ease, color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
  }
  .btn:focus-visible { outline: none; box-shadow: 0 0 0 3px var(--focus-glow); }
  .btn:disabled { opacity: 0.55; cursor: not-allowed; }
  .sm { min-height: 36px; padding: 0.4rem 0.8rem; font-size: 0.85rem; }
  .md { padding: 0.65rem 1.15rem; font-size: 0.95rem; }
  .lg { padding: 0.85rem 1.6rem; font-size: 1.05rem; }
  .icon { padding: 0; width: 44px; }
  .primary { background: var(--accent); color: #fff; border-color: var(--accent-deep); box-shadow: var(--shadow-sm); }
  .primary:hover:not(:disabled) { background: var(--accent-deep); box-shadow: var(--shadow), 0 2px 8px color-mix(in srgb, var(--accent) 30%, transparent); }
  .primary:active:not(:disabled) { background: color-mix(in srgb, var(--accent-deep) 88%, var(--ink)); border-color: color-mix(in srgb, var(--accent-deep) 88%, var(--ink)); transform: translateY(1px); box-shadow: none; }
  .primary:hover:not(:disabled):focus-visible { box-shadow: 0 0 0 3px var(--focus-glow), 0 2px 8px color-mix(in srgb, var(--accent) 30%, transparent); }
  .primary:active:not(:disabled):focus-visible { box-shadow: 0 0 0 3px var(--focus-glow); }
  .ghost { background: transparent; color: var(--ink); border-color: var(--line-strong); }
  .ghost:hover:not(:disabled) { background: var(--paper-2); }
  .destructive { background: var(--danger); color: #fff; border-color: var(--danger-deep); }
  .destructive:hover:not(:disabled) { background: var(--danger-deep); }
  .link { background: transparent; color: var(--accent-deep); border-color: transparent; padding-inline: 0; min-height: 0; }
  .link:hover:not(:disabled) { text-decoration: underline; }
  .spinner {
    width: 0.9em; height: 0.9em; border-radius: 50%;
    border: 2px solid currentColor; border-top-color: transparent;
    display: inline-block; animation: spin 0.7s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
</style>
