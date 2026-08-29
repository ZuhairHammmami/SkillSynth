<!-- Admin system health page: reads GET /admin/reports/system-health. -->
<script lang="ts">
  import { apiFetch, ApiError } from '$lib/api/client';
  import { query, invalidate } from '$lib/query';
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
      data = await query(['HEALTH'], () => apiFetch('/admin/reports/system-health'));
    } catch (e) {
      err = e instanceof ApiError ? e.detail : t('admin.common.failedLoad', { entity: t('admin.nav.systemHealth') });
    } finally { loading = false; }
  }
  $effect(() => { load(); });

  function refresh() { invalidate(['HEALTH']); load(); }
</script>

<h1>{t('admin.health.title')}</h1>

{#if loading}
  <div class="c"><Spinner /></div>
{:else if err}
  <Panel>
    <div class="err-box" role="alert">
      <p>{err}</p>
      <Button variant="ghost" onclick={refresh}><Icon name="refresh" size={15} /> {t('common.retry')}</Button>
    </div>
  </Panel>
{:else}
  <Panel>
    <div class="stats">
      <div class="stat">
        <span class="k">{t('admin.common.databaseStatus')}</span>
        <span class="v" class:ok={data.database_status === 'Connected'} class:bad={data.database_status !== 'Connected'}>
          {data.database_status === 'Connected' ? t('admin.health.databaseConnected') : t('admin.health.databaseDown')}
        </span>
      </div>
      <div class="stat">
        <span class="k">{t('admin.health.apiVersion')}</span>
        <span class="v">{data.api_version ?? '—'}</span>
      </div>
      <div class="stat">
        <span class="k">{t('admin.health.totalUsers')}</span>
        <span class="v">{data.total_users ?? '—'}</span>
      </div>
      <div class="stat">
        <span class="k">{t('admin.health.totalPaths')}</span>
        <span class="v">{data.total_paths ?? '—'}</span>
      </div>
      <div class="stat">
        <span class="k">{t('admin.health.totalAssessments')}</span>
        <span class="v">{data.total_assessments ?? '—'}</span>
      </div>
    </div>
    {#if data.details && Object.keys(data.details).length}
      <div class="details">
        <h3>{t('admin.health.details')}</h3>
        <ul>
          {#each Object.entries(data.details) as [k, v]}
            <li><strong>{k}</strong>: {String(v)}</li>
          {/each}
        </ul>
      </div>
    {/if}
    <div class="foot">
      <Button variant="ghost" onclick={refresh}><Icon name="refresh" size={15} /> {t('common.retry')}</Button>
    </div>
  </Panel>
{/if}

<style>
  .c { padding: 3rem 0; text-align: center; }
  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1rem; }
  .stat { display: flex; flex-direction: column; gap: 0.3rem; padding: 0.9rem 1rem; border: 1px solid var(--line); border-radius: var(--radius); }
  .k { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); }
  .v { font-size: 1.1rem; font-weight: 700; }
  .v.ok { color: var(--ok, #15803d); }
  .v.bad { color: var(--danger); }
  .details { margin-top: 1.2rem; }
  .details h3 { font-size: 0.9rem; margin-bottom: 0.4rem; }
  .details ul { margin: 0; padding-inline-start: 1.2rem; font-size: 0.9rem; color: var(--ink-soft); }
  .foot { margin-top: 1.2rem; }
  .err-box { background: var(--danger-soft); border: 1px solid var(--danger); color: var(--danger); padding: 1rem; border-radius: var(--radius); display: flex; flex-direction: column; gap: 0.6rem; }
</style>
