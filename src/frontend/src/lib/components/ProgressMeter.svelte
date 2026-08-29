<!-- Hairline progress meter. Warm-craft alternative to a filled bar. -->
<script lang="ts">
  let { value = 0, label = '' }: { value?: number; label?: string } = $props();
  let pct = $derived(Math.max(0, Math.min(100, Math.round(value))));
</script>

<div class="meter">
  <div class="track"><div class="fill" style="inline-size: {pct}%"></div></div>
  {#if label}<span class="lbl">{label} · {pct}%</span>{/if}
</div>

<style>
  .meter { display: flex; flex-direction: column; gap: 0.3rem; }
  .track { height: 8px; background: var(--paper-2); border: 1px solid var(--line); border-radius: 999px; overflow: hidden; }
  .fill { height: 100%; background: linear-gradient(90deg, var(--accent), var(--accent-deep)); border-radius: 999px; transition: inline-size 0.4s ease; }
  .lbl { font-size: 0.78rem; color: var(--muted); }
</style>
