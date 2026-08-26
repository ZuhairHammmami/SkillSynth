<!-- Analytics dashboard. -->
<script lang="ts">
  import { apiFetch } from '$lib/api/client';
  import { query } from '$lib/query';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import ProgressMeter from '$lib/components/ProgressMeter.svelte';
  import TopSkills from '$lib/components/TopSkills.svelte';
  import { t } from '$lib/i18n';

  let dash = $state<any>(null);
  let growth = $state<any[]>([]);
  let loading = $state(true);
  async function load() {
    loading = true;
    try {
      [dash, growth] = await Promise.all([
        query(['analyticsDashboard'], () => apiFetch('/analytics/dashboard')),
        query(['skillGrowth'], () => apiFetch('/analytics/skill-growth'))
      ]);
    } finally { loading = false; }
  }
  $effect(() => { load(); });
</script>

<h1>{t('analyticsPage.title')}</h1>
<p class="muted">{t('analyticsPage.subtitle')}</p>

{#if loading}
  <div class="center-spin"><Spinner /></div>
{:else}
  <div class="stats">
    <Panel title={t('analyticsPage.completion')}>
      <div class="big">{Math.round(dash?.completion_rate ?? 0)}%</div>
      <ProgressMeter value={dash?.completion_rate ?? 0} />
    </Panel>
    <Panel title={t('analyticsPage.masteredSkills')}>
      <div class="big">{dash?.mastered_skills ?? 0}</div>
    </Panel>
    <Panel title={t('analyticsPage.learningVelocity')}>
      <div class="big">{Math.round(dash?.learning_velocity ?? 0)}<small>/wk</small></div>
    </Panel>
  </div>

  <div class="grid2">
    <Panel title={t('analyticsPage.pathsOverview')}>
      <ul class="kpis">
        <li><span>{t('dashboardPage.yourPaths')}</span><strong>{dash?.paths_count ?? 0}</strong></li>
        <li><span>{t('dashboardPage.completed')}</span><strong>{dash?.completed_steps ?? 0}</strong></li>
        <li><span>{t('dashboardPage.learningHours')}</span><strong>{Math.round(dash?.learning_hours ?? 0)}h</strong></li>
      </ul>
    </Panel>
    <Panel title={t('analyticsPage.weaknesses')}>
      {#if dash?.weaknesses?.length}
        <div class="weak">{#each dash.weaknesses as w}<Badge tone="clay">{w}</Badge>{/each}</div>
      {:else}
        <p class="muted">{t('analyticsPage.weaknessNote')}</p>
      {/if}
    </Panel>
  </div>

  <Panel title={t('analyticsPage.practiceTest')}>
    <TopSkills items={growth ?? []} />
  </Panel>
{/if}

<style>
  .center-spin { display: flex; justify-content: center; padding: 3rem; }
  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem; }
  .big { font-family: var(--font-display); font-size: 2.2rem; color: var(--ochre-deep); line-height: 1; }
  .big small { font-size: 1rem; color: var(--muted); }
  .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem; }
  .kpis { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.6rem; }
  .kpis li { display: flex; justify-content: space-between; border-bottom: 1px dashed var(--line); padding-bottom: 0.4rem; }
  .weak { display: flex; flex-wrap: wrap; gap: 0.4rem; }
  @media (max-width: 760px) { .grid2 { grid-template-columns: 1fr; } }
</style>
