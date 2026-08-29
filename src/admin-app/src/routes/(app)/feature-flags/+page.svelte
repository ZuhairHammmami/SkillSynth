<!-- Admin feature flags, schema-driven. Loads the flat flag map PLUS the
     FLAG_SCHEMA registry and renders per-type controls driven entirely by the
     schema metadata. Edits stage locally; one bulk PUT /feature-flags sends
     only the dirty keys; 422 places inline per-field errors and rolls inputs
     back to the last-fetched values. Row shells + per-type controls live in
     FlagRow / FlagControl. -->
<script lang="ts">
  import { apiFetch, ApiError, fieldErrorsFrom } from '$lib/api/client';
  import { query, invalidate } from '$lib/query';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Icon from '$lib/icons/Icon.svelte';
  import FlagRow from '$lib/components/FlagRow.svelte';
  import FlagControl from '$lib/components/FlagControl.svelte';
  import { success, error as toastError } from '$lib/components/ui/toast';
  import { t } from '$lib/i18n';

  let flags = $state<any>(null);
  let schema = $state<any>(null);
  let staged = $state<any>(null);
  let corsText = $state('');
  let errors = $state<Record<string, string>>({});
  let loading = $state(true);
  let saving = $state(false);
  let err = $state<string | null>(null);

  function listToText(list: any): string {
    return Array.isArray(list) ? list.join('\n') : '';
  }

  function deepEqual(a: any, b: any): boolean {
    if (a === b) return true;
    if (typeof a !== typeof b) return false;
    if (Array.isArray(a) && Array.isArray(b)) {
      if (a.length !== b.length) return false;
      return a.every((x, i) => deepEqual(x, b[i]));
    }
    if (a && b && typeof a === 'object' && typeof b === 'object') {
      const ka = Object.keys(a);
      const kb = Object.keys(b);
      if (ka.length !== kb.length) return false;
      return ka.every((k) => Object.prototype.hasOwnProperty.call(b, k) && deepEqual(a[k], b[k]));
    }
    return false;
  }

  const dirty = $derived(
    staged && flags ? Object.keys(flags).some((k) => !deepEqual(staged[k], flags[k])) : false
  );

  const schemaEntries = $derived<any[][]>(schema ? Object.entries(schema) : []);

  function stage(key: string, value: any): void {
    staged = { ...staged, [key]: value };
    if (errors[key]) {
      const e = { ...errors };
      delete e[key];
      errors = e;
    }
  }

  function onFlagUpdate(key: string, value: any): void {
    const meta = schema[key];
    if (meta.type === 'list[str]') {
      corsText = value;
      value = value
        .split('\n')
        .map((s: string) => s.trim())
        .filter((s: string) => s.length > 0);
    }
    stage(key, value);
  }

  async function load(): Promise<void> {
    loading = true;
    err = null;
    try {
      const [f, s] = await Promise.all([
        query(['FLAGS'], () => apiFetch('/admin/feature-flags')),
        query(['FLAG_SCHEMA'], () => apiFetch('/admin/feature-flags/schema'))
      ]);
      flags = f;
      schema = s;
      staged = { ...f };
      corsText = listToText(f.cors_origins);
      errors = {};
    } catch (e) {
      err = e instanceof ApiError ? e.detail : t('admin.common.failedLoad', { entity: t('admin.nav.featureFlags') });
    } finally {
      loading = false;
    }
  }

  $effect(() => { load(); });

  async function save(): Promise<void> {
    if (!dirty || saving || !flags) return;
    saving = true;
    try {
      const payload: Record<string, any> = {};
      for (const k of Object.keys(flags)) {
        if (!deepEqual(staged[k], flags[k])) payload[k] = staged[k];
      }
      const resp = await apiFetch('/admin/feature-flags', { method: 'PUT', body: payload });
      flags = resp;
      staged = { ...resp };
      corsText = listToText(resp.cors_origins);
      errors = {};
      invalidate(['FLAGS']);
      success(t('admin.flags.saved'));
    } catch (e) {
      staged = { ...flags };
      corsText = listToText(flags.cors_origins);
      errors = e instanceof ApiError && e.rawDetail ? fieldErrorsFrom(e.rawDetail) : {};
      toastError(e instanceof ApiError ? e.detail : t('admin.common.saveFailed'));
    } finally {
      saving = false;
    }
  }

  function discard(): void {
    if (!flags) return;
    staged = { ...flags };
    corsText = listToText(flags.cors_origins);
    errors = {};
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
{:else if flags && schema}
  <Panel title={t('admin.flags.title')} subtitle={t('admin.flags.subtitle')}>
    {#each schemaEntries as [key, meta]}
      <FlagRow {key} {meta} value={staged[key]} error={errors[key]}>
        <FlagControl {key} {meta} value={meta.type === 'list[str]' ? corsText : staged[key]} error={errors[key]} onupdate={onFlagUpdate} />
      </FlagRow>
    {/each}
  </Panel>

  <div class="savebar">
    {#if dirty}<span class="dirty-hint" role="status">{t('admin.flags.unsavedChanges')}</span>{/if}
    <div class="actions">
      <Button variant="ghost" onclick={discard} disabled={!dirty || saving}>{t('admin.flags.discard')}</Button>
      <Button variant="primary" onclick={save} disabled={!dirty} loading={saving}>{t('admin.flags.save')}</Button>
    </div>
  </div>
{/if}

<style>
  .c { padding: 3rem 0; text-align: center; }

  .savebar { display: flex; align-items: center; justify-content: space-between; gap: 1rem; margin-top: 1.25rem; padding: 1rem 0.25rem; }
  .actions { display: flex; gap: 0.75rem; }
  .dirty-hint { font-size: 0.85rem; color: var(--warn); }
  .err-box { background: var(--danger-soft); border: 1px solid var(--danger); color: var(--danger); padding: 1rem; border-radius: var(--radius); display: flex; flex-direction: column; gap: 0.6rem; }
</style>
