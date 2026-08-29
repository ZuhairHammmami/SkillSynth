<!-- Admin DB inspector: table row counts from GET /db-inspector with a
     refresh button. -->
<script lang="ts">
  import { apiFetch, ApiError } from '$lib/api/client';
  import { query } from '$lib/query';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Icon from '$lib/icons/Icon.svelte';
  import { t } from '$lib/i18n';

  let data = $state<any>(null);
  let loading = $state(true);
  let err = $state<string | null>(null);

  async function load(): Promise<void> {
    loading = true;
    err = null;
    try {
      data = await query(['DB'], () => apiFetch('/admin/db-inspector'));
    } catch (e) { err = e instanceof ApiError ? e.detail : t('admin.common.failedLoad', { entity: t('admin.nav.dbInspector') }); }
    finally { loading = false; }
  }

  $effect(() => { load(); });

  function refresh(): void { load(); }
</script>

<h1>{t('admin.dbInspector.title')}</h1>

{#if loading}
  <div class="c"><Spinner /></div>
{:else if err}
  <Panel>
    <div class="err-box" role="alert">
      <p>{err}</p>
      <Button variant="ghost" onclick={load}><Icon name="refresh" size={15} /> {t('common.retry')}</Button>
    </div>
  </Panel>
{:else if data}
  <Panel>
    <div class="head">
      <p class="muted">{t('admin.dbInspector.summary', { database: data.database ?? 'skillsynth.db', count: data.total_tables ?? 0, size: data.size_formatted ?? '—', integrity: data.integrity_check ? t('admin.dbInspector.ok') : t('admin.dbInspector.fail') })}</p>
      <Button variant="ghost" onclick={refresh}><Icon name="refresh" size={15} /> {t('admin.common.refresh')}</Button>
    </div>
    <div class="table-scroll">
      <table class="tbl">
        <thead>
          <tr><th>{t('admin.common.table')}</th><th>{t('admin.common.rowsLabel')}</th><th>{t('admin.common.columns')}</th></tr>
        </thead>
        <tbody>
          {#each (data.tables ?? []) as tbl}
            <tr>
              <td>{tbl.table}</td>
              <td>{tbl.rows ?? 0}</td>
              <td>{(tbl.columns ?? []).map((c: any) => c.name).join(', ')}</td>
            </tr>
          {/each}
          {#if (data.tables ?? []).length === 0}
            <tr><td colspan="3" class="empty">{t('admin.dbInspector.empty')}</td></tr>
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
  .empty { color: var(--clay); text-align: center; }
  .err-box { background: var(--danger-soft); border: 1px solid var(--danger); color: var(--danger); padding: 1rem; border-radius: var(--radius); display: flex; flex-direction: column; gap: 0.6rem; }
</style>
