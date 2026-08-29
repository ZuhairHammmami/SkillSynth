<!-- Toast viewport. Subscribes to the toast store; tints derive from status
     tokens (accent-soft / ok-soft / danger-soft) with token borders. -->
<script lang="ts">
  import { toasts } from './toast';
</script>

<div class="toaster" aria-live="polite" role="status">
  {#each $toasts as t (t.id)}
    <div class="toast {t.type}">{t.message}</div>
  {/each}
</div>

<style>
  .toaster {
    position: fixed; top: 1rem; inset-inline-start: 50%; transform: translateX(-50%);
    display: flex; flex-direction: column; gap: 0.5rem; z-index: 100; width: min(420px, 92vw);
  }
  .toast {
    padding: 0.7rem 1rem; border-radius: var(--radius); font-size: 0.9rem; font-weight: 500;
    border: 1px solid var(--line-strong); background: var(--paper); color: var(--ink);
    box-shadow: var(--shadow);
  }
  .success { border-color: var(--ok); background: var(--ok-soft); color: var(--ok); }
  .error { border-color: var(--danger); background: var(--danger-soft); color: var(--danger); }
  .info { border-color: var(--accent); background: var(--accent-soft); color: var(--accent-deep); }
</style>
