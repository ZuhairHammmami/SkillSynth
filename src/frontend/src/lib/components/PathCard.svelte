<!-- Path card. Shows title, goal, progress and step/hours summary. -->
<script lang="ts">
  import { goto } from '$app/navigation';
  import type { Path } from '$lib/types/api';
  import ProgressMeter from './ProgressMeter.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import { t } from '$lib/i18n';

  let { path }: { path: Path } = $props();
  let steps = $derived(path.steps ?? []);
  let done = $derived(steps.filter((s) => s.is_completed).length);
  let hours = $derived(steps.reduce((a, s) => a + (s.duration_hours ?? 0), 0));
</script>

<button class="card" onclick={() => goto(`/learn/${path.id}`)}>
  <div class="head">
    <h3>{path.title}</h3>
    <Badge tone="accent">{path.goal_job_role ?? path.goal ?? ''}</Badge>
  </div>
  <ProgressMeter value={(path.progress ?? 0) * 100} />
  <div class="meta">
    <span>{done}/{steps.length} {t('units.steps')}</span>
    <span>·</span>
    <span>{hours} {t('units.hoursShort')}</span>
  </div>
</button>

<style>
  .card { text-align: start; background: var(--card); border: 1px solid var(--line); border-radius: var(--radius-lg); padding: 1.1rem; cursor: pointer; display: flex; flex-direction: column; gap: 0.7rem; width: 100%; font-family: var(--font-body); color: var(--ink); transition: border-color 0.18s ease, box-shadow 0.18s ease; }
  .card:hover { border-color: var(--ochre); text-decoration: none; box-shadow: var(--shadow); }
  .card:focus-visible { outline: none; box-shadow: 0 0 0 3px var(--focus-glow); border-color: var(--ochre); }
  .card:active { transform: translateY(1px); }
  .head { display: flex; flex-direction: column; gap: 0.4rem; }
  .head h3 { margin: 0; font-size: 1.15rem; }
  .meta { display: flex; gap: 0.4rem; font-size: 0.82rem; color: var(--clay); }
</style>
