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

<button class="btn {variant} {size}" {type} {disabled} {onclick} {...rest}>
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
    line-height: 1;
    transition: transform 0.06s ease, background 0.15s ease, border-color 0.15s ease;
  }
  .btn:active { transform: translateY(1px); }
  .btn:disabled { opacity: 0.55; cursor: not-allowed; }
  .sm { padding: 0.4rem 0.7rem; font-size: 0.82rem; }
  .md { padding: 0.6rem 1.1rem; font-size: 0.95rem; }
  .lg { padding: 0.8rem 1.5rem; font-size: 1.05rem; }
  .primary { background: var(--ochre); color: #fff7e8; border-color: var(--ochre-deep); }
  .primary:hover:not(:disabled) { background: var(--ochre-deep); }
  .ghost { background: transparent; color: var(--ink); border-color: var(--line-strong); }
  .ghost:hover:not(:disabled) { background: var(--paper-2); }
  .destructive { background: var(--danger); color: #fff; border-color: #7e2c1c; }
  .destructive:hover:not(:disabled) { background: #7e2c1c; }
  .link { background: transparent; color: var(--ochre-deep); border-color: transparent; padding-inline: 0; }
  .link:hover:not(:disabled) { text-decoration: underline; }
  .spinner {
    width: 0.9em; height: 0.9em; border-radius: 50%;
    border: 2px solid currentColor; border-top-color: transparent;
    display: inline-block; animation: spin 0.7s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
</style>
