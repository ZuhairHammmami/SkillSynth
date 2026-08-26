<!-- Student dashboard. Pulls progress, paths, and analytics; refreshes on SSE. -->
<script lang="ts">
  import { apiFetch } from '$lib/api/client';
  import { query, invalidate } from '$lib/query';
  import { goto } from '$app/navigation';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Icon from '$lib/icons/Icon.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import ProgressMeter from '$lib/components/ProgressMeter.svelte';
  import PathCard from '$lib/components/PathCard.svelte';
  import { t } from '$lib/i18n';

  let dash = $state<any>(null);
  let paths = $state<any[]>([]);
  let analytics = $state<any>(null);
  let loading = $state(true);

  async function load() {
    loading = true;
    try {
      [dash, paths, analytics] = await Promise.all([
        query(['dashboard'], () => apiFetch('/progress/dashboard')),
        query(['paths'], () => apiFetch('/paths/')),
        query(['analyticsDashboard'], () => apiFetch('/analytics/dashboard'))
      ]);
    } finally {
      loading = false;
    }
  }
  $effect(() => {
    load();
    const h = () => { invalidate(['dashboard']); invalidate(['paths']); load(); };
    window.addEventListener('sse:path_generated', h);
    return () => window.removeEventListener('sse:path_generated', h);
  });
</script>

<h1>{t('dashboardPage.title')}</h1>
<p class="muted">{t('dashboardPage.subtitle')}</p>

{#if loading}
  <div class="center-spin"><Spinner /></div>
{:else}
  <div class="stats">
    <Panel title={t('dashboardPage.completionRate')}>
      <div class="big">{Math.round(dash?.completion_rate ?? 0)}%</div>
      <ProgressMeter value={dash?.completion_rate ?? 0} />
    </Panel>
    <Panel title={t('dashboardPage.learningHours')}>
      <div class="big">{Math.round(dash?.learning_hours ?? 0)}<small>h</small></div>
      <p class="muted">{t('dashboardPage.stepsOf', { done: dash?.completed_steps ?? 0, total: dash?.total_steps ?? 0 })}</p>
    </Panel>
    <Panel title={t('dashboardPage.yourPaths')}>
      <div class="big">{paths.length}</div>
      <p class="muted">{(dash?.paths_count ?? paths.length)}</p>
    </Panel>
  </div>

  <h2 class="section-title">{t('dashboardPage.yourPaths')}</h2>
  {#if paths.length === 0}
    <Panel>
      <p class="muted">{t('dashboardPage.noPaths')}</p>
      <button class="link" onclick={() => goto('/wizard')}>{t('dashboardPage.createFirstPath')}</button>
    </Panel>
  {:else}
    <div class="cards">
      {#each paths.slice(0, 3) as p}<PathCard path={p} />{/each}
    </div>
  {/if}

  <h2 class="section-title">{t('dashboardPage.recentActivity')}</h2>
  <Panel>
    {#if dash?.recent_activity?.length}
      <ul class="activity">
        {#each dash.recent_activity.slice(0, 6) as a}
          <li><Icon name="check" size={16} /><span>{a.title ?? a.message ?? 'Activity'}</span></li>
        {/each}
      </ul>
    {:else}
      <p class="muted">{t('dashboardPage.noRecentActivity')}</p>
    {/if}
  </Panel>
{/if}

<style>
  .center-spin { display: flex; justify-content: center; padding: 3rem; }
  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-top: 1rem; }
  .big { font-family: var(--font-display); font-size: 2.2rem; color: var(--ochre-deep); line-height: 1; }
  .big small { font-size: 1rem; color: var(--muted); }
  .section-title { margin-top: 2rem; font-size: 1.3rem; }
  .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1rem; }
  .activity { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.6rem; }
  .activity li { display: flex; align-items: center; gap: 0.5rem; color: var(--ink-soft); }
  .activity :global(svg) { color: var(--sage); }
</style>
