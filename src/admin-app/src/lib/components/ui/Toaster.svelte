<!-- Toast viewport. Subscribes to the toast store. -->
<script lang="ts">
  import { toasts } from './toast';
</script>

<div class="toaster" aria-live="polite">
  {#each $toasts as t (t.id)}
    <div class="toast {t.type}">{t.message}</div>
  {/each}
</div>

<style>
  .toaster {
    position: fixed; top: 1rem; left: 50%; transform: translateX(-50%);
    display: flex; flex-direction: column; gap: 0.5rem; z-index: 100; width: min(420px, 92vw);
  }
  .toast {
    padding: 0.7rem 1rem; border-radius: var(--radius); font-size: 0.9rem; font-weight: 500;
    border: 1px solid var(--line-strong); background: var(--paper); color: var(--ink);
    box-shadow: 0 6px 24px rgba(42, 37, 33, 0.15);
  }
  .success { border-color: var(--sage); background: #f1f5ec; }
  .error { border-color: var(--danger); background: #fbeeea; color: var(--danger); }
  .info { border-color: var(--ochre); background: #fbf2e0; }
</style>
