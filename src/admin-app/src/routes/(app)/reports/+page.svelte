<!-- Admin reports: aggregated metrics + system health in two panels. -->
<script lang="ts">
  import { apiFetch, ApiError } from '$lib/api/client';
  import { query } from '$lib/query';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Icon from '$lib/icons/Icon.svelte';
  import { t } from '$lib/i18n';

  let agg = $state<any>(null);
  let health = $state<any>(null);
  let loading = $state(true);
  let err = $state<string | null>(null);

  function fmt(v: any): string {
    if (v === null || v === undefined) return '—';
    if (typeof v === 'boolean') return v ? t('admin.common.yes') : t('admin.common.no');
    return String(v);
  }

  async function load(): Promise<void> {
    loading = true;
    err = null;
    try {
      const [a, h] = await Promise.all([
        query(['REP_AGG'], () => apiFetch('/admin/reports/aggregated')),
        query(['REP_HEALTH'], () => apiFetch('/admin/reports/system-health'))
      ]);
      agg = a;
      health = h;
    } catch (e) { err = e instanceof ApiError ? e.detail : t('admin.common.failedLoad', { entity: t('admin.nav.reports') }); }
    finally { loading = false; }
  }

  $effect(() => { load(); });

  const aggCards = $derived([
    { label: t('admin.reports.hoursLearned'), value: fmt(agg?.total_hours_learned) },
    { label: t('admin.reports.avgCompletion'), value: fmt(agg?.average_completion_rate) + '%' },
    { label: t('admin.reports.assessmentAttempts'), value: fmt(agg?.total_assessment_attempts) },
    { label: t('admin.reports.avgScore'), value: fmt(agg?.average_assessment_score) }
  ]);

  const healthRows = $derived([
    { k: t('admin.common.databaseStatus'), v: health?.database_status },
    { k: t('admin.common.apiVersion'), v: health?.api_version },
    { k: t('admin.common.totalUsers'), v: health?.total_users },
    { k: t('admin.common.totalPaths'), v: health?.total_paths },
    { k: t('admin.common.totalAssessments'), v: health?.total_assessments }
  ]);
</script>

<h1>{t('admin.reports.title')}</h1>

{#if loading}
  <div class="c"><Spinner /></div>
{:else if err}
  <Panel>
    <div class="err-box" role="alert">
      <p>{err}</p>
      <Button variant="ghost" onclick={load}><Icon name="refresh" size={15} /> {t('common.retry')}</Button>
    </div>
  </Panel>
{:else}
  <div class="grid">
    <Panel title={t('admin.reports.aggregated')} subtitle={t('admin.reports.platformWide')}>
      <div class="cards">
        {#each aggCards as c}
          <div class="stat">
            <span class="stat-v">{c.value}</span>
            <span class="stat-l">{c.label}</span>
          </div>
        {/each}
      </div>
      {#if agg?.most_active_users?.length}
        <h4 class="sub">{t('admin.reports.mostActive')}</h4>
        <ul class="mini">
          {#each agg.most_active_users as u}
            <li><span>{fmt(u.user_email)}</span><b>{t('admin.reports.steps', { n: fmt(u.completed_steps) })}</b></li>
          {/each}
        </ul>
      {/if}
    </Panel>

    <Panel title={t('admin.reports.systemHealth')} subtitle={t('admin.reports.serviceStatus')}>
      <ul class="kv">
        {#each healthRows as r}
          <li><span>{r.k}</span><b>{fmt(r.v)}</b></li>
        {/each}
      </ul>
    </Panel>
  </div>
{/if}

<style>
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; }
  .c { padding: 3rem 0; text-align: center; }
  .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 0.8rem; }
  .stat { display: flex; flex-direction: column; gap: 0.25rem; padding: 0.8rem; border: 1px solid var(--line); border-radius: var(--radius); background: var(--paper-2); }
  .stat-v { font-size: 1.5rem; font-weight: 700; color: var(--ink); }
  .stat-l { font-size: 0.8rem; color: var(--muted); }
  .sub { margin: 1.2rem 0 0.5rem; font-size: 0.9rem; color: var(--ink-soft); }
  .mini { list-style: none; margin: 0; padding: 0; display: grid; gap: 0.3rem; }
  .mini li { display: flex; justify-content: space-between; font-size: 0.85rem; padding: 0.3rem 0; border-bottom: 1px dashed var(--line); }
  .mini li span { color: var(--muted); }
  .kv { list-style: none; margin: 0; padding: 0; display: grid; gap: 0.4rem; }
  .kv li { display: flex; justify-content: space-between; gap: 1rem; font-size: 0.92rem; padding: 0.3rem 0; border-bottom: 1px dashed var(--line); }
  .kv li span { color: var(--muted); }
  .err-box { background: var(--danger-soft); border: 1px solid var(--danger); color: var(--danger); padding: 1rem; border-radius: var(--radius); display: flex; flex-direction: column; gap: 0.6rem; }
</style>
