<!-- Admin feature flags, schema-driven. Loads the flat flag map PLUS the
     FLAG_SCHEMA registry and renders per-type controls driven entirely by the
     schema metadata. Edits stage locally; one bulk PUT /feature-flags sends
     only the dirty keys; 422 places inline per-field errors and rolls inputs
     back to the last-fetched values. -->
<script lang="ts">
  import { apiFetch, ApiError, fieldErrorsFrom } from '$lib/api/client';
  import { query, invalidate } from '$lib/query';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Icon from '$lib/icons/Icon.svelte';
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

  function stageBool(key: string, value: boolean): void { stage(key, value); }
  function stageStr(key: string, value: string): void { stage(key, value); }
  function stageInt(key: string, raw: string): void {
    const n = Number(raw);
    if (raw === '' || Number.isNaN(n)) return;
    stage(key, n);
  }
  function stageList(raw: string): void {
    corsText = raw;
    const items = raw.split('\n').map((s) => s.trim()).filter((s) => s.length > 0);
    stage('cors_origins', items);
  }
  function stagePolicy(data: Record<string, any>): void {
    stage('password_policy', { ...staged.password_policy, ...data });
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

  function displayValue(key: string, meta: any): string {
    const v = staged[key];
    if (meta.type === 'bool') return v ? t('admin.flags.on') : t('admin.flags.off');
    if (Array.isArray(v)) return v.join(', ');
    if (v && typeof v === 'object') return JSON.stringify(v);
    return String(v ?? '');
  }

  function badgeFor(meta: any): { label: string; tone: string } | null {
    if (!meta.editable) return { label: t('admin.flags.readOnlyBadge'), tone: 'neutral' };
    if (meta.restart) return { label: t('admin.flags.appliesAfterRestart'), tone: 'warn' };
    if (meta.live) return { label: t('admin.flags.live'), tone: 'ok' };
    return null;
  }

  function typeLabel(meta: any): string {
    if (meta.type === 'bool') return t('admin.flags.typeBool');
    if (meta.type === 'int') return t('admin.flags.typeInt');
    if (meta.type === 'str') return t('admin.flags.typeStr');
    if (meta.type === 'list[str]') return t('admin.flags.typeListStr');
    return t('admin.flags.typeObject');
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
      {@const badge = badgeFor(meta)}
      <div class="flag {!meta.editable ? 'readonly' : ''}">
        <div class="head">
          <div class="label">
            <span class="k">{key}</span>
            <span class="type">{typeLabel(meta)}</span>
          </div>
          {#if badge}<Badge tone={badge.tone}>{badge.label}</Badge>{/if}
        </div>

        {#if !meta.editable}
          <div class="value">{displayValue(key, meta)}</div>
        {:else if meta.type === 'bool'}
          <label class="switch">
            <input type="checkbox" checked={staged[key]} onchange={(e) => stageBool(key, (e.currentTarget as HTMLInputElement).checked)} aria-label={t('admin.flags.toggle', { key })} />
            <span class="track"></span>
          </label>
          {#if errors[key]}<span class="err" role="alert">{errors[key]}</span>{/if}
        {:else if meta.type === 'int'}
          <div class="field">
            <input class="ctl" type="number" inputmode="numeric" value={staged[key]} min={meta.min} max={meta.max}
                   aria-label={key} aria-invalid={errors[key] ? 'true' : undefined}
                   oninput={(e) => stageInt(key, (e.currentTarget as HTMLInputElement).value)} />
            {#if errors[key]}<span class="err" role="alert">{errors[key]}</span>{/if}
          </div>
        {:else if meta.type === 'str'}
          <div class="field">
            <input class="ctl" type="text" value={staged[key]} maxlength={meta.max_length}
                   aria-label={key} aria-invalid={errors[key] ? 'true' : undefined}
                   oninput={(e) => stageStr(key, (e.currentTarget as HTMLInputElement).value)} />
            {#if key === 'ai_local_model'}<span class="hint">{t('admin.flags.modelPatternHint')}</span>{/if}
            {#if errors[key]}<span class="err" role="alert">{errors[key]}</span>{/if}
          </div>
        {:else if meta.type === 'list[str]'}
          <div class="field">
            <textarea class="ctl" rows={3} value={corsText} aria-label={key}
                      oninput={(e) => stageList((e.currentTarget as HTMLTextAreaElement).value)}></textarea>
            <span class="hint">{t('admin.flags.corsOriginHint')}</span>
            {#if errors[key]}<span class="err" role="alert">{errors[key]}</span>{/if}
          </div>
        {:else if meta.type === 'object'}
          <div class="object-group">
            <span class="og-label">{t('admin.flags.passwordPolicy')}</span>
            <label class="og-min">
              <span>{t('admin.flags.minLength')}</span>
              <input class="ctl" type="number" inputmode="numeric" min={6} max={32} value={staged[key]?.min_length}
                     aria-label={t('admin.flags.minLength')} aria-invalid={errors[key] ? 'true' : undefined}
                     oninput={(e) => stagePolicy({ min_length: Number((e.currentTarget as HTMLInputElement).value) })} />
            </label>
            <div class="og-toggles">
              {#each [['require_uppercase', 'requireUppercase'], ['require_lowercase', 'requireLowercase'], ['require_digit', 'requireDigit'], ['require_special_char', 'requireSpecialChar']] as [sub, label]}
                <div class="switch-row">
                  <span>{t('admin.flags.' + label)}</span>
                  <label class="switch">
                    <input type="checkbox" checked={staged[key]?.[sub]} onchange={(e) => stagePolicy({ [sub]: (e.currentTarget as HTMLInputElement).checked })} aria-label={t('admin.flags.' + label)} />
                    <span class="track"></span>
                  </label>
                </div>
              {/each}
            </div>
            {#if errors[key]}<span class="err" role="alert">{errors[key]}</span>{/if}
          </div>
        {/if}
      </div>
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
  .flag { padding: 0.8rem 0; border-bottom: 1px dashed var(--line); }
  .flag.readonly { opacity: 0.85; }
  .head { display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
  .label { display: flex; flex-direction: column; gap: 0.15rem; }
  .k { font-weight: 600; color: var(--ink); }
  .type { font-size: 0.75rem; color: var(--muted); }
  .value { margin-top: 0.4rem; font-size: 0.85rem; color: var(--ink-soft); word-break: break-word; }
  .field { margin-top: 0.5rem; max-width: 560px; }
  .ctl {
    width: 100%; font-family: var(--font-body); font-size: 0.95rem; color: var(--ink);
    background: var(--paper); border: 1px solid var(--line-strong); border-radius: var(--radius);
    padding: 0.55rem 0.7rem; min-height: 40px; box-sizing: border-box;
  }
  textarea.ctl { resize: vertical; font-family: var(--font-mono, monospace); }
  .ctl:focus-visible { outline: none; border-color: var(--ring); box-shadow: 0 0 0 3px var(--focus-glow); }
  .ctl[aria-invalid='true'] { border-color: var(--danger); }
  .hint { display: block; color: var(--muted); font-size: 0.78rem; margin-top: 0.25rem; }
  .err { display: block; color: var(--danger); font-size: 0.78rem; margin-top: 0.3rem; }

  .object-group { margin-top: 0.5rem; max-width: 560px; }
  .og-label { display: block; font-size: 0.82rem; font-weight: 600; color: var(--ink-soft); margin-bottom: 0.5rem; }
  .og-min { display: flex; align-items: center; gap: 0.75rem; font-size: 0.85rem; color: var(--ink-soft); }
  .og-min .ctl { max-width: 96px; }
  .og-toggles { margin-top: 0.6rem; display: grid; gap: 0.55rem; }
  .switch-row { display: flex; align-items: center; justify-content: space-between; gap: 1rem; font-size: 0.85rem; color: var(--ink); }

  .switch { position: relative; display: inline-block; width: 44px; height: 24px; flex-shrink: 0; }
  .switch input { opacity: 0; width: 0; height: 0; }
  .switch input:focus-visible + .track { outline: 2px solid var(--ring); outline-offset: 2px; }
  .track { position: absolute; inset: 0; background: var(--line-strong); border-radius: 999px; transition: background 0.15s; }
  .track::before { content: ''; position: absolute; inset-inline-start: 3px; top: 3px; width: 18px; height: 18px; background: var(--paper); border-radius: 50%; transition: inset-inline-start 0.15s; }
  .switch input:checked + .track { background: var(--accent); }
  .switch input:checked + .track::before { inset-inline-start: 23px; }

  .savebar { display: flex; align-items: center; justify-content: space-between; gap: 1rem; margin-top: 1.25rem; padding: 1rem 0.25rem; }
  .actions { display: flex; gap: 0.75rem; }
  .dirty-hint { font-size: 0.85rem; color: var(--warn); }
  .err-box { background: var(--danger-soft); border: 1px solid var(--danger); color: var(--danger); padding: 1rem; border-radius: var(--radius); display: flex; flex-direction: column; gap: 0.6rem; }
</style>
