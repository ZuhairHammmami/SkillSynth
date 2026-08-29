<!-- Status badge. Variants: neutral | accent | ok | danger | warn. Each uses
     sufficient-contrast token pairings (dark text on a light tint). -->
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
    border: 1px solid var(--line-strong);
    background: var(--paper-2);
    color: var(--ink-soft);
    white-space: nowrap;
  }
  .neutral { background: var(--paper-2); color: var(--ink-soft); border-color: var(--line-strong); }
  .accent { background: var(--ochre-soft); color: var(--ochre-deep); border-color: var(--ochre); }
  .danger { background: var(--danger-soft); color: var(--danger); border-color: var(--danger); }
  .ok { background: var(--ok-soft); color: var(--ok); border-color: var(--ok); }
  .warn { background: color-mix(in srgb, var(--warn) 14%, var(--card)); color: var(--warn); border-color: var(--warn); }
</style>
