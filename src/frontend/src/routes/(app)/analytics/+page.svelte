<!-- Comprehensive analytics dashboard: KPIs, this-week activity, path progress,
     strengths vs weaknesses, knowledge gaps, and skill mastery. -->
<script lang="ts">
  import { apiFetch, ApiError } from '$lib/api/client';
  import { query } from '$lib/query';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import ProgressMeter from '$lib/components/ProgressMeter.svelte';
  import TopSkills from '$lib/components/TopSkills.svelte';
  import ActivityBarChart from '$lib/components/ActivityBarChart.svelte';
  import Icon from '$lib/icons/Icon.svelte';
  import { error as toastError } from '$lib/components/ui/toast';
  import { t } from '$lib/i18n';

  let dash = $state<any>(null);
  let growth = $state<any>(null);
  let analysis = $state<any>(null);
  let history = $state<any>(null);
  let loading = $state(true);
  let loadError = $state('');
  async function load() {
    loading = true;
    loadError = '';
    try {
      [dash, growth, analysis, history] = await Promise.all([
        query(['analyticsDashboard'], () => apiFetch('/analytics/dashboard')),
        query(['skillGrowth'], () => apiFetch('/analytics/skill-growth')),
        query(['skillAnalysis'], () => apiFetch('/learning/analysis')),
        query(['learningHistory'], () => apiFetch('/analytics/learning-history'))
      ]);
    } catch (e) {
      loadError = e instanceof ApiError ? e.detail : t('analytics.loadError');
      toastError(loadError);
    } finally { loading = false; }
  }
  $effect(() => { load(); });
</script>

<h1>{t('analyticsPage.title')}</h1>
<p class="muted">{t('analyticsPage.subtitle')}</p>

{#if loading}
  <div class="center-spin"><Spinner /></div>
{:else if loadError}
  <Panel>
    <div class="err-state">
      <Icon name="alert" size={22} />
      <p>{loadError}</p>
      <Button onclick={load}>{t('common.retry')}</Button>
    </div>
  </Panel>
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
      <div class="big">{Math.round(dash?.learning_velocity ?? 0)}<small>{t('units.perWeek')}</small></div>
    </Panel>
    <Panel title={t('analyticsPage.learningHours')}>
      <div class="big">{Math.round(dash?.learning_hours ?? 0)}<small>{t('units.hoursShort')}</small></div>
    </Panel>
  </div>

  <div class="grid2">
    <Panel title={t('analyticsPage.thisWeek')}>
      <ActivityBarChart data={history?.daily_activity ?? []} />
    </Panel>
    <Panel title={t('analyticsPage.knowledgeGaps')}>
      {#if growth?.items?.some((g: any) => g.status === 'not_started')}
        <div class="wrap">{#each growth.items.filter((g: any) => g.status === 'not_started') as g}<Badge tone="warn">{g.skill}</Badge>{/each}</div>
      {:else}
        <p class="muted">{t('analyticsPage.noKnowledgeGaps')}</p>
      {/if}
    </Panel>
  </div>

  <Panel title={t('analyticsPage.pathsOverview')}>
    {#if dash?.path_progress?.length}
      <ul class="paths">
        {#each dash.path_progress as p}
          <li>
            <div class="phead">
              <span class="pname">{p.path_title}</span>
              <span class="pmut">{p.completed_steps}/{p.total_steps} · {p.percentage}%</span>
            </div>
            <ProgressMeter value={p.percentage} />
          </li>
        {/each}
      </ul>
    {:else}
      <p class="muted">{t('analyticsPage.noPaths')}</p>
    {/if}
  </Panel>

  <div class="grid2">
    <Panel title={t('analyticsPage.strengths')}>
      {#if analysis?.strengths?.length}
        <div class="wrap">{#each analysis.strengths as s}<Badge tone="ok">{s.skill_name}</Badge>{/each}</div>
      {:else}
        <p class="muted">{t('analyticsPage.noStrengths')}</p>
      {/if}
    </Panel>
    <Panel title={t('analyticsPage.weaknesses')}>
      {#if analysis?.weaknesses?.length}
        <div class="wrap">{#each analysis.weaknesses as w}<Badge tone="accent">{w.skill_name}</Badge>{/each}</div>
      {:else}
        <p class="muted">{t('analyticsPage.noWeaknesses')}</p>
      {/if}
    </Panel>
  </div>

  <Panel title={t('analyticsPage.practiceTest')}>
    <TopSkills
      items={(growth?.items ?? []).map((s: any) => ({
        skill: s.skill,
        proficiency: s.level,
        status: s.status
      }))}
    />
  </Panel>
{/if}

<style>
  .center-spin { display: flex; justify-content: center; padding: 3rem; }
  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 1rem; margin-top: 1rem; }
  .big { font-family: var(--font-display); font-size: 2.2rem; color: var(--ochre-deep); line-height: 1; }
  .big small { font-size: 1rem; color: var(--clay); }
  .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem; }
  .wrap { display: flex; flex-wrap: wrap; gap: 0.4rem; }
  .paths { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.9rem; }
  .phead { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.3rem; gap: 1rem; }
  .pname { font-weight: 600; }
  .pmut { font-size: 0.78rem; color: var(--clay); white-space: nowrap; }
  .err-state { display: flex; flex-direction: column; align-items: flex-start; gap: 0.6rem; color: var(--danger); }
  @media (max-width: 760px) { .grid2 { grid-template-columns: 1fr; } }
</style>
