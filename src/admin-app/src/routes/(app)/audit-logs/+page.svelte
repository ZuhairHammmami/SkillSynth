<!-- Admin audit logs: activity feed from GET /events plus live sse:activity
     prepending new entries, a 30s periodic reconcile, and a manual Refresh
     button. -->
<script lang="ts">
  import { apiFetch, ApiError } from '$lib/api/client';
  import { invalidate, query } from '$lib/query';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Icon from '$lib/icons/Icon.svelte';
  import { t } from '$lib/i18n';

  const POLL_MS = 30_000;

  let rows = $state<any[]>([]);
  let loading = $state(true);
  let err = $state<string | null>(null);

  function fmt(v: any): string {
    if (v === null || v === undefined) return '—';
    return String(v);
  }

  async function load(silent = false): Promise<void> {
    if (!silent) loading = true;
    err = null;
    try {
      const d = await query(['EVT'], () => apiFetch('/admin/events', { query: { limit: 50 } }));
      rows = Array.isArray(d) ? d : [];
    } catch (e) { err = e instanceof ApiError ? e.detail : t('admin.common.failedLoad', { entity: t('admin.nav.auditLogs') }); }
    finally { if (!silent) loading = false; }
  }

  async function refresh(): Promise<void> {
    invalidate(['EVT']);
    await load(true);
  }

  $effect(() => {
    load();
    const h = (e: any) => {
      const detail = e?.detail ?? {};
      rows = [detail, ...rows].slice(0, 100);
    };
    window.addEventListener('sse:activity', h as EventListener);
    const poll = setInterval(() => { invalidate(['EVT']); load(true); }, POLL_MS);
    return () => {
      window.removeEventListener('sse:activity', h as EventListener);
      clearInterval(poll);
    };
  });
</script>

<div class="head">
  <h1>{t('admin.auditLogs.title')}</h1>
  <Button variant="ghost" onclick={refresh}><Icon name="refresh" size={15} /> {t('admin.common.refresh')}</Button>
</div>

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
  <Panel title={t('admin.auditLogs.activityLog')} subtitle={t('admin.auditLogs.subtitle')}>
    <ul class="feed" aria-live="polite">
      {#each rows as ev (ev.id ?? ev.created_at ?? Math.random())}
        <li>
          <Icon name="activity" size={15} />
          <span class="act">{fmt(ev.action ?? ev.category) || t('admin.common.event')}</span>
          <span class="meta">{fmt(ev.user_email)}</span>
          <span class="meta">{fmt(ev.created_at)}</span>
        </li>
      {/each}
      {#if rows.length === 0}
        <li class="empty">{t('admin.auditLogs.noActivity')}</li>
      {/if}
    </ul>
  </Panel>
{/if}

<style>
  .head { display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
  .c { padding: 3rem 0; text-align: center; }
  .feed { list-style: none; margin: 0; padding: 0; display: grid; gap: 0.3rem; max-height: 70vh; overflow: auto; }
  .feed li { display: flex; align-items: center; gap: 0.6rem; font-size: 0.88rem; padding: 0.4rem 0; border-bottom: 1px dashed var(--line); }
  .feed .act { color: var(--ink); font-weight: 600; text-transform: capitalize; }
  .feed .meta { color: var(--clay); margin-inline-start: auto; font-size: 0.8rem; }
  .feed .empty { color: var(--clay); }
  .err-box { background: var(--danger-soft); border: 1px solid var(--danger); color: var(--danger); padding: 1rem; border-radius: var(--radius); display: flex; flex-direction: column; gap: 0.6rem; }
</style>