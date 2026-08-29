<!-- Badge / tag. Status pills with sufficient contrast. -->
<script lang="ts">
  let { tone = 'neutral', children }: any = $props();
</script>

<span class="badge {tone}">{@render children()}</span>

<style>
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.2rem 0.6rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    line-height: 1.3;
    border: 1px solid var(--line-strong);
    background: var(--paper-2);
    color: var(--ink-soft);
  }
  .neutral { background: var(--paper-2); color: var(--ink-soft); }
  .accent { background: var(--accent); color: #fff; border-color: var(--accent-deep); }
  .ok { background: var(--ok-soft); color: var(--ok); border-color: var(--ok); }
  .danger { background: var(--danger-soft); color: var(--danger); border-color: var(--danger); }
  .warn { background: var(--warn-soft); color: var(--warn); border-color: var(--warn); }
</style>
