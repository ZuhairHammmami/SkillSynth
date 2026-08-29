<!-- Admin backups: create a snapshot (POST /backups) and list existing ones
     with a download button opening the backup URL in a new tab. -->
<script lang="ts">
  import { apiFetch, ApiError } from '$lib/api/client';
  import { query, invalidate } from '$lib/query';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Icon from '$lib/icons/Icon.svelte';
  import { success, error as toastError } from '$lib/components/ui/toast';
  import { t } from '$lib/i18n';

  let rows = $state<any[]>([]);
  let loading = $state(true);
  let err = $state<string | null>(null);
  let creating = $state(false);

  async function load(): Promise<void> {
    loading = true;
    err = null;
    try {
      const d = await query(['BK'], () => apiFetch('/admin/backups'));
      rows = Array.isArray(d) ? d : [];
    } catch (e) { err = e instanceof ApiError ? e.detail : t('admin.common.failedLoad', { entity: t('admin.nav.backups') }); }
    finally { loading = false; }
  }

  $effect(() => { load(); });

  async function create(): Promise<void> {
    creating = true;
    try {
      await apiFetch('/admin/backups', { method: 'POST' });
      invalidate(['BK']);
      await load();
      success(t('admin.backups.created'));
    } catch (e) {
      toastError(e instanceof ApiError ? e.detail : t('admin.common.deleteFailed'));
    } finally {
      creating = false;
    }
  }

  function download(name: string): void {
    window.open('/api/admin/backups/' + encodeURIComponent(name), '_blank');
  }
</script>

<h1>{t('admin.backups.title')}</h1>

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
    <div class="head">
      <p class="muted">{t('admin.backups.snapshotHint')}</p>
      <Button onclick={create} loading={creating}><Icon name="download" size={15} /> {t('admin.backups.create')}</Button>
    </div>
    <div class="table-scroll">
      <table class="tbl">
        <thead>
          <tr><th>{t('admin.common.file')}</th><th>{t('admin.common.size')}</th><th>{t('admin.common.created')}</th><th></th></tr>
        </thead>
        <tbody>
          {#each rows as r}
            <tr>
              <td>{r.path ?? r.name ?? '—'}</td>
              <td>{r.size_formatted ?? r.size_bytes ?? '—'}</td>
              <td>{r.created_at ?? '—'}</td>
              <td class="right"><Button variant="ghost" size="sm" onclick={() => download(r.path ?? r.name)}><Icon name="download" size={14} /> {t('admin.common.download')}</Button></td>
            </tr>
          {/each}
          {#if rows.length === 0}
            <tr><td colspan="4" class="empty">{t('admin.backups.empty')}</td></tr>
          {/if}
        </tbody>
      </table>
    </div>
  </Panel>
{/if}

<style>
  .c { padding: 3rem 0; text-align: center; }
  .head { display: flex; align-items: center; justify-content: space-between; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap; }
  .muted { color: var(--clay); font-size: 0.85rem; margin: 0; }
  .table-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  .tbl { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
  .tbl th, .tbl td { text-align: start; padding: 0.55rem 0.6rem; border-bottom: 1px solid var(--line); }
  .tbl th { color: var(--clay); font-weight: 600; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.03em; }
  .right { text-align: end; }
  .empty { color: var(--clay); text-align: center; }
  .err-box { background: var(--danger-soft); border: 1px solid var(--danger); color: var(--danger); padding: 1rem; border-radius: var(--radius); display: flex; flex-direction: column; gap: 0.6rem; }
</style>
