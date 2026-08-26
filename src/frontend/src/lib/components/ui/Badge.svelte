<!-- Badge / tag. Warm-craft pill with tone variants. -->
<script lang="ts">
  let { tone = 'neutral', children }: any = $props();
</script>

<span class="badge {tone}">{@render children()}</span>

<style>
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.15rem 0.55rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    border: 1px solid var(--line-strong);
    background: var(--paper-2);
    color: var(--ink-soft);
  }
  .neutral { background: var(--paper-2); }
  .ochre { background: var(--ochre); color: #fff7e8; border-color: var(--ochre-deep); }
  .sage { background: var(--sage); color: #f3f6ee; border-color: var(--sage-deep); }
  .danger { background: var(--danger); color: #fff; border-color: #7e2c1c; }
  .warn { background: #efd9a6; color: var(--ochre-deep); border-color: var(--ochre); }
  .ok { background: var(--sage); color: #f3f6ee; border-color: var(--sage-deep); }
</style>
