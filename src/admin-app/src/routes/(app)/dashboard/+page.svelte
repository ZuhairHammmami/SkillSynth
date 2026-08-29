<!-- Admin dashboard: system health + aggregated metrics, plus a live activity
     ticker fed by GET /events and the sse:activity bus. -->
<script lang="ts">
  import { apiFetch, ApiError } from '$lib/api/client';
  import { query } from '$lib/query';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Icon from '$lib/icons/Icon.svelte';
  import { t } from '$lib/i18n';

  let health = $state<any>(null);
  let agg = $state<any>(null);
  let activity = $state<any[]>([]);
  let loading = $state(true);
  let err = $state<string | null>(null);

  function fmt(v: any): string {
    if (v === null || v === undefined) return '—';
    if (typeof v === 'number') return String(v);
    if (typeof v === 'boolean') return v ? t('admin.common.yes') : t('admin.common.no');
    return String(v);
  }

  async function load(): Promise<void> {
    loading = true;
    err = null;
    try {
      const [h, a, ev] = await Promise.all([
        query(['HEALTH'], () => apiFetch('/admin/reports/system-health')),
        query(['AGG'], () => apiFetch('/admin/reports/aggregated')),
        query(['DASH_EVT'], () => apiFetch('/admin/events', { query: { limit: 12 } }))
      ]);
      health = h;
      agg = a;
      activity = Array.isArray(ev) ? ev : [];
    } catch (e) { err = e instanceof ApiError ? e.detail : t('admin.common.failedLoad', { entity: t('admin.nav.dashboard') }); }
    finally { loading = false; }
  }

  $effect(() => {
    load();
    const h = (e: any) => {
      const detail = e?.detail ?? {};
      activity = [detail, ...activity].slice(0, 30);
    };
    window.addEventListener('sse:activity', h as EventListener);
    return () => window.removeEventListener('sse:activity', h as EventListener);
  });

  const aggCards = $derived([
    { label: t('admin.reports.hoursLearned'), value: fmt(agg?.total_hours_learned) },
    { label: t('admin.reports.avgCompletion'), value: fmt(agg?.average_completion_rate) + '%' },
    { label: t('admin.reports.assessmentAttempts'), value: fmt(agg?.total_assessment_attempts) },
    { label: t('admin.reports.avgScore'), value: fmt(agg?.average_assessment_score) }
  ]);
</script>

<h1>{t('admin.dashboard.title')}</h1>

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
    <Panel title={t('admin.dashboard.platformOverview')} subtitle={t('admin.dashboard.aggregatedMetrics')}>
      <div class="cards">
        {#each aggCards as c}
          <div class="stat">
            <span class="stat-v">{c.value}</span>
            <span class="stat-l">{c.label}</span>
          </div>
        {/each}
      </div>
    </Panel>

    <Panel title={t('admin.dashboard.systemHealth')} subtitle={t('admin.dashboard.serviceStatus')}>
      <ul class="kv">
        <li><span>{t('admin.common.databaseStatus')}</span><b>{fmt(health?.database_status)}</b></li>
        <li><span>{t('admin.common.apiVersion')}</span><b>{fmt(health?.api_version)}</b></li>
        <li><span>{t('admin.common.totalUsers')}</span><b>{fmt(health?.total_users)}</b></li>
        <li><span>{t('admin.common.totalPaths')}</span><b>{fmt(health?.total_paths)}</b></li>
        <li><span>{t('admin.common.totalAssessments')}</span><b>{fmt(health?.total_assessments)}</b></li>
      </ul>
    </Panel>
  </div>

  <div class="mt">
    <Panel title={t('admin.dashboard.activity')} subtitle={t('admin.dashboard.liveStream')}>
      <ul class="feed" aria-live="polite">
        {#each activity as ev (ev.id ?? ev.created_at ?? Math.random())}
          <li>
            <Icon name="activity" size={15} />
            <span class="act">{fmt(ev.action ?? ev.category) || t('admin.common.event')}</span>
            <span class="meta">{fmt(ev.user_email)}</span>
            <span class="meta">{fmt(ev.created_at)}</span>
          </li>
        {/each}
        {#if activity.length === 0}
          <li class="empty">{t('admin.dashboard.noActivity')}</li>
        {/if}
      </ul>
    </Panel>
  </div>
{/if}

<style>
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }
  .mt { margin-top: 1rem; }
  .c { padding: 3rem 0; text-align: center; }
  .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 0.8rem; }
  .stat { display: flex; flex-direction: column; gap: 0.25rem; padding: 0.8rem; border: 1px solid var(--line); border-radius: var(--radius); background: var(--paper-2); }
  .stat-v { font-size: 1.5rem; font-weight: 700; color: var(--ink); }
  .stat-l { font-size: 0.8rem; color: var(--clay); }
  .kv { list-style: none; margin: 0; padding: 0; display: grid; gap: 0.4rem; }
  .kv li { display: flex; justify-content: space-between; gap: 1rem; font-size: 0.92rem; padding: 0.3rem 0; border-bottom: 1px dashed var(--line); }
  .kv li span { color: var(--clay); }
  .feed { list-style: none; margin: 0; padding: 0; display: grid; gap: 0.3rem; }
  .feed li { display: flex; align-items: center; gap: 0.6rem; font-size: 0.88rem; padding: 0.4rem 0; border-bottom: 1px dashed var(--line); }
  .feed .act { color: var(--ink); font-weight: 600; }
  .feed .meta { color: var(--clay); margin-inline-start: auto; font-size: 0.8rem; }
  .feed .empty { color: var(--clay); }
  .err-box { background: var(--danger-soft); border: 1px solid var(--danger); color: var(--danger); padding: 1rem; border-radius: var(--radius); display: flex; flex-direction: column; gap: 0.6rem; }
</style>
