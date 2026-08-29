<!-- Styled data table wrapper. Adds zebra striping (tokens), th scope, and
     keeps overflow contained so the page never scrolls horizontally at 375px. -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  let { children }: any = $props();
</script>

<div class="table-wrap">
  <table class="ss-table">{@render children()}</table>
</div>

<style>
  .table-wrap {
    overflow-x: auto;
    border: 1px solid var(--line);
    border-radius: var(--radius-lg);
    background: var(--card);
    -webkit-overflow-scrolling: touch;
  }
  .ss-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
  .ss-table :global(th) {
    text-align: start; font-weight: 600; color: var(--ink-soft);
    background: var(--paper-2); padding: 0.7rem 0.9rem; border-bottom: 1px solid var(--line-strong);
    white-space: nowrap;
  }
  .ss-table :global(td) { padding: 0.7rem 0.9rem; border-bottom: 1px solid var(--line); vertical-align: middle; }
  .ss-table :global(tbody tr:nth-child(even)) { background: var(--paper-2); }
  .ss-table :global(tbody tr:last-child td) { border-bottom: none; }
  .ss-table :global(tbody tr:hover) { background: var(--ochre-soft); }
</style>
