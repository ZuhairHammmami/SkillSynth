<!-- Student dashboard. Fetches analytics + learning history + paths in
     parallel; refreshes the same three queries on the sse:path_generated
     event. KPI row via StatCard, this-week chart, recent activity, paths. -->
<script lang="ts">
  import { apiFetch, ApiError } from '$lib/api/client';
  import { query, invalidate } from '$lib/query';
  import { goto } from '$app/navigation';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Icon from '$lib/icons/Icon.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import PathCard from '$lib/components/PathCard.svelte';
  import StatCard from '$lib/components/StatCard.svelte';
  import ActivityBarChart from '$lib/components/ActivityBarChart.svelte';
  import RecentActivity from '$lib/components/RecentActivity.svelte';
  import { error as toastError } from '$lib/components/ui/toast';
  import { t } from '$lib/i18n';

  let dash = $state<any>(null);
  let history = $state<any>(null);
  let paths = $state<any[]>([]);
  let loading = $state(true);
  let loadError = $state('');

  async function load() {
    loading = true;
    loadError = '';
    try {
      [dash, history, paths] = await Promise.all([
        query(['analyticsDashboard'], () => apiFetch('/analytics/dashboard')),
        query(['learningHistory'], () => apiFetch('/analytics/learning-history')),
        query(['paths'], () => apiFetch('/paths/'))
      ]);
    } catch (e) {
      loadError = e instanceof ApiError ? e.detail : t('dashboardPage.errorDesc');
      toastError(loadError);
    } finally {
      loading = false;
    }
  }
  $effect(() => {
    load();
    const h = () => {
      invalidate(['analyticsDashboard']);
      invalidate(['learningHistory']);
      invalidate(['paths']);
      load();
    };
    window.addEventListener('sse:path_generated', h);
    return () => window.removeEventListener('sse:path_generated', h);
  });

  const hours = $derived.by(() => {
    const v = Number(dash?.learning_hours ?? 0);
    return v % 1 === 0 ? String(Math.round(v)) : v.toFixed(1);
  });
  const steps = $derived.by(() => ({
    done: (paths ?? []).reduce(
      (a, p) => a + (p.steps ?? []).filter((s: any) => s.is_completed).length,
      0
    ),
    total: (paths ?? []).reduce((a, p) => a + (p.steps ?? []).length, 0)
  }));
  const displayPaths = $derived(
    (paths ?? []).map((p: any) => {
      const matched = dash?.path_progress?.find((pp: any) => pp.path_id === p.id);
      return matched ? { ...p, progress: (matched.percentage ?? 0) / 100 } : p;
    })
  );
  const activityItems = $derived(
    (dash?.recent_activity ?? []).map((a: any, i: number) => ({
      id: a.date ?? i,
      title: a.description,
      message: a.description,
      created_at: a.date
    }))
  );
</script>

<h1>{t('dashboardPage.title')}</h1>
<p class="muted">{t('dashboardPage.subtitle')}</p>

{#if loading}
  <div class="center-spin"><Spinner /></div>
{:else if loadError}
  <Panel>
    <div class="err-state">
      <Icon name="alert" size={22} />
      <p>{t('dashboardPage.errorTitle')}</p>
      <p class="muted">{t('dashboardPage.errorDesc')}</p>
      <Button onclick={load}>{t('common.retry')}</Button>
    </div>
  </Panel>
{:else}
  <div class="stats">
    <StatCard
      label={t('dashboardPage.completionRate')}
      value={`${Math.round(dash?.completion_rate ?? 0)}%`}
      hint={t('dashboardPage.completionsThisWeek', { count: dash?.weekly_completions ?? 0 })}
      icon="check"
      muted={(dash?.completion_rate ?? 0) === 0}
    />
    <StatCard
      label={t('dashboardPage.learningHours')}
      value={`${hours} ${t('units.hoursShort')}`}
      hint={t('dashboardPage.stepsOf', { done: steps.done, total: steps.total })}
      icon="clock"
      muted={(dash?.learning_hours ?? 0) === 0}
    />
    <StatCard
      label={t('analyticsPage.masteredSkills')}
      value={dash?.mastered_skills ?? 0}
      hint={t('dashboardPage.inProgress', { count: dash?.learning_skills ?? 0 })}
      icon="star"
      muted={(dash?.mastered_skills ?? 0) === 0}
    />
    <StatCard
      label={t('analyticsPage.learningVelocity')}
      value={`${Math.round(dash?.learning_velocity ?? 0)}${t('units.perWeek')}`}
      hint={t('dashboardPage.completionsThisWeek', { count: dash?.weekly_completions ?? 0 })}
      icon="trending"
      muted={(dash?.learning_velocity ?? 0) === 0}
    />
  </div>

  <h2 class="section-title">{t('analyticsPage.thisWeek')}</h2>
  <Panel>
    <ActivityBarChart data={history?.daily_activity ?? []} />
  </Panel>

  <h2 class="section-title">{t('dashboardPage.recentActivity')}</h2>
  <Panel>
    <RecentActivity items={activityItems} empty={t('dashboardPage.noRecentActivity')} />
  </Panel>

  <div class="paths-head">
    <h2 class="section-title">{t('dashboardPage.yourPaths')}</h2>
    <Button variant="link" onclick={() => goto('/analytics')}>
      {t('dashboardPage.viewAnalytics')}
    </Button>
  </div>
  {#if displayPaths.length === 0}
    <Panel>
      <p class="muted">{t('dashboardPage.noPaths')}</p>
      <button class="link" onclick={() => goto('/wizard')}>{t('dashboardPage.createFirstPath')}</button>
    </Panel>
  {:else}
    <div class="cards">
      {#each displayPaths as p}<PathCard path={p} />{/each}
    </div>
  {/if}
{/if}

<style>
  .center-spin { display: flex; justify-content: center; padding: 3rem; }
  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-top: 1rem; }
  .section-title { margin-top: 2rem; font-size: 1.3rem; }
  .paths-head { display: flex; align-items: center; gap: 1rem; }
  .paths-head .section-title { margin-top: 2rem; flex: 1; }
  .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1rem; }
  .link { background: none; border: none; padding: 0; font: inherit; color: var(--accent-deep); cursor: pointer; text-decoration: underline; }
  .err-state { display: flex; flex-direction: column; align-items: flex-start; gap: 0.6rem; color: var(--danger); }
  .err-state .muted { color: var(--muted); }
</style>