<!-- Styled table. Plain <table class="ss-table"> in pages; this wrapper adds
     warm-craft chrome (hairline rules, generous spacing). -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  let { children }: any = $props();
</script>

<div class="table-wrap">
  <table class="ss-table">{@render children()}</table>
</div>

<style>
  .table-wrap { overflow-x: auto; border: 1px solid var(--line); border-radius: var(--radius-lg); }
  .ss-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
  .ss-table :global(th) {
    text-align: start; font-weight: 600; color: var(--ink-soft);
    background: var(--paper-2); padding: 0.7rem 0.9rem; border-bottom: 1px solid var(--line-strong);
  }
  .ss-table :global(td) { padding: 0.7rem 0.9rem; border-bottom: 1px solid var(--line); vertical-align: middle; }
  .ss-table :global(tr:last-child td) { border-bottom: none; }
  .ss-table :global(tbody tr:hover) { background: rgba(181, 134, 46, 0.05); }
</style>
