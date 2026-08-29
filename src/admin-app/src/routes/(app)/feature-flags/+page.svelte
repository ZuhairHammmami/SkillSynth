<!-- Admin feature flags: read GET /feature-flags and toggle the AI flag via
     PUT /feature-flags ({ ai_enabled }). Other flags are read-only. Optimistic
     update with rollback on failure. -->
<script lang="ts">
  import { apiFetch, ApiError } from '$lib/api/client';
  import { query } from '$lib/query';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Icon from '$lib/icons/Icon.svelte';
  import { success, error as toastError } from '$lib/components/ui/toast';
  import { t } from '$lib/i18n';

  let flags = $state<any>(null);
  let loading = $state(true);
  let err = $state<string | null>(null);
  let saving = $state(false);

  async function load(): Promise<void> {
    loading = true;
    err = null;
    try {
      flags = await query(['FLAGS'], () => apiFetch('/admin/feature-flags'));
    } catch (e) { err = e instanceof ApiError ? e.detail : t('admin.common.failedLoad', { entity: t('admin.nav.featureFlags') }); }
    finally { loading = false; }
  }

  $effect(() => { load(); });

  async function toggleAi(value: boolean): Promise<void> {
    const previous = flags;
    saving = true;
    try {
      await apiFetch('/admin/feature-flags', { method: 'PUT', body: { ai_enabled: value } });
      flags = { ...flags, ai_enabled: value, ai_path_generation: value };
      success(t('admin.flags.updated'));
    } catch (e) {
      flags = previous;
      toastError(e instanceof ApiError ? e.detail : t('admin.common.saveFailed'));
    } finally {
      saving = false;
    }
  }

  function display(v: any): string {
    if (typeof v === 'boolean') return v ? t('admin.flags.on') : t('admin.flags.off');
    if (Array.isArray(v)) return v.join(', ');
    if (v && typeof v === 'object') return JSON.stringify(v);
    return String(v);
  }
</script>

<h1>{t('admin.flags.title')}</h1>

{#if loading}
  <div class="c"><Spinner /></div>
{:else if err}
  <Panel>
    <div class="err-box" role="alert">
      <p>{err}</p>
      <Button variant="ghost" onclick={load}><Icon name="refresh" size={15} /> {t('common.retry')}</Button>
    </div>
  </Panel>
{:else if flags}
  <Panel title={t('admin.flags.title')} subtitle={t('admin.flags.subtitle')}>
    <ul class="flags">
      {#each Object.entries(flags) as [key, val]}
        <li>
          <div class="label">
            <span class="k">{key}</span>
            {#if typeof val === 'boolean'}
              <span class="v">{val ? t('admin.flags.on') : t('admin.flags.off')}</span>
            {:else}
              <span class="v plain">{display(val)}</span>
            {/if}
          </div>
          {#if key === 'ai_enabled'}
            <label class="switch">
              <input type="checkbox" checked={val as boolean} disabled={saving} onchange={(e) => toggleAi((e.currentTarget as HTMLInputElement).checked)} aria-label={t('admin.flags.toggle', { key })} />
              <span class="track"></span>
            </label>
          {:else if typeof val === 'boolean'}
            <label class="switch">
              <input type="checkbox" checked={val as boolean} disabled aria-label={t('admin.common.readOnly', { key })} />
              <span class="track"></span>
            </label>
          {:else}
            <span class="dash">—</span>
          {/if}
        </li>
      {/each}
    </ul>
  </Panel>
{/if}

<style>
  .c { padding: 3rem 0; text-align: center; }
  .flags { list-style: none; margin: 0; padding: 0; display: grid; gap: 0.2rem; }
  .flags li { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 0.7rem 0; border-bottom: 1px dashed var(--line); }
  .label { display: flex; flex-direction: column; gap: 0.15rem; }
  .k { font-weight: 600; color: var(--ink); }
  .v { font-size: 0.8rem; color: var(--accent-deep); font-weight: 600; }
  .v.plain { color: var(--muted); font-weight: 500; }
  .dash { color: var(--muted); }
  .switch { position: relative; display: inline-block; width: 44px; height: 24px; flex-shrink: 0; }
  .switch input { opacity: 0; width: 0; height: 0; }
  .switch input:focus-visible + .track { outline: 2px solid var(--ring); outline-offset: 2px; }
  .track { position: absolute; inset: 0; background: var(--line-strong); border-radius: 999px; transition: background 0.15s; }
  .track::before { content: ''; position: absolute; inset-inline-start: 3px; top: 3px; width: 18px; height: 18px; background: var(--paper); border-radius: 50%; transition: inset-inline-start 0.15s; }
  .switch input:checked + .track { background: var(--accent); }
  .switch input:checked + .track::before { inset-inline-start: 23px; }
  .switch input:disabled + .track { opacity: 0.6; }
  .err-box { background: var(--danger-soft); border: 1px solid var(--danger); color: var(--danger); padding: 1rem; border-radius: var(--radius); display: flex; flex-direction: column; gap: 0.6rem; }
</style>
