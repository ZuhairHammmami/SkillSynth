<!-- Path card. Shows title, goal, progress and step/hours summary. -->
<script lang="ts">
  import { goto } from '$app/navigation';
  import type { Path } from '$lib/types/api';
  import ProgressMeter from './ProgressMeter.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';

  let { path }: { path: Path } = $props();
  let steps = $derived(path.steps ?? []);
  let done = $derived(steps.filter((s) => s.completed).length);
  let hours = $derived(steps.reduce((a, s) => a + (s.duration_hours ?? 0), 0));
</script>

<button class="card" onclick={() => goto(`/learn/${path.id}`)}>
  <div class="head">
    <h3>{path.title}</h3>
    <Badge tone="ochre">{path.goal}</Badge>
  </div>
  <ProgressMeter value={path.progress ?? 0} />
  <div class="meta">
    <span>{done}/{steps.length} steps</span>
    <span>·</span>
    <span>{hours}h</span>
  </div>
</button>

<style>
  .card { text-align: start; background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); padding: 1.1rem; cursor: pointer; display: flex; flex-direction: column; gap: 0.7rem; width: 100%; font-family: var(--font-body); color: var(--ink); transition: border-color 0.15s, transform 0.06s; }
  .card:hover { border-color: var(--ochre); text-decoration: none; }
  .card:active { transform: translateY(1px); }
  .head { display: flex; flex-direction: column; gap: 0.4rem; }
  .head h3 { margin: 0; font-size: 1.15rem; }
  .meta { display: flex; gap: 0.4rem; font-size: 0.82rem; color: var(--muted); }
</style>
