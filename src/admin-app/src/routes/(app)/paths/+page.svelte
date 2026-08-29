<!-- Admin paths table: live admin listing from GET /admin/paths, refreshed
     manually, on error-retry, and on the sse:path_generated DOM event. -->
<script lang="ts">
  import { apiFetch, ApiError } from '$lib/api/client';
  import { invalidate, query } from '$lib/query';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Icon from '$lib/icons/Icon.svelte';
  import { t } from '$lib/i18n';

  let rows = $state<any[]>([]);
  let loading = $state(true);
  let err = $state<string | null>(null);

  async function load(): Promise<void> {
    loading = true;
    err = null;
    try {
      const d = await query(['PATHS'], () => apiFetch('/admin/paths'));
      rows = Array.isArray(d) ? d : [];
    } catch (e) { err = e instanceof ApiError ? e.detail : t('admin.common.failedLoad', { entity: t('admin.nav.paths') }); }
    finally { loading = false; }
  }

  async function refresh(): Promise<void> {
    invalidate(['PATHS']);
    await load();
  }

  $effect(() => {
    load();
    const h = () => { invalidate(['PATHS']); load(); };
    window.addEventListener('sse:path_generated', h);
    return () => window.removeEventListener('sse:path_generated', h);
  });
</script>

<div class="head">
  <h1>{t('admin.paths.title')}</h1>
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
  <Panel>
    <div class="table-scroll">
      <table class="tbl">
        <thead>
          <tr><th>{t('admin.common.id')}</th><th>{t('admin.common.title')}</th><th>{t('admin.common.owner')}</th><th>{t('admin.common.hours')}</th><th>{t('admin.common.completed')}</th><th>{t('admin.common.created')}</th></tr>
        </thead>
        <tbody>
          {#each rows as r}
            <tr>
              <td>{r.id}</td>
              <td>{r.title ?? '—'}</td>
              <td>{r.user_email ?? '—'}</td>
              <td>{r.total_estimated_hours ?? '—'}</td>
              <td>
                {#if r.is_completed}<Badge tone="ok">{t('admin.common.completed')}</Badge>
                {:else}<Badge tone="warn">{t('admin.common.inProgress')}</Badge>{/if}
              </td>
              <td>{r.created_at ?? '—'}</td>
            </tr>
          {/each}
          {#if rows.length === 0}
            <tr><td colspan="6" class="empty">{t('admin.paths.empty')}</td></tr>
          {/if}
        </tbody>
      </table>
    </div>
  </Panel>
{/if}

<style>
  .head { display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
  .c { padding: 3rem 0; text-align: center; }
  .table-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  .tbl { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
  .tbl th, .tbl td { text-align: start; padding: 0.55rem 0.6rem; border-bottom: 1px solid var(--line); }
  .tbl th { color: var(--clay); font-weight: 600; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.03em; }
  .empty { color: var(--clay); text-align: center; }
  .err-box { background: var(--danger-soft); border: 1px solid var(--danger); color: var(--danger); padding: 1rem; border-radius: var(--radius); display: flex; flex-direction: column; gap: 0.6rem; }
</style>