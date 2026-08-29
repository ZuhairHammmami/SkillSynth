<!-- FlagControl: per-type schema-driven feature-flag control. Renders the
     switch (bool), number input (int), text input (str), one-URL-per-line
     textarea (list[str]) or the nested password-policy group (object).
     Emits the next staged value up via the onupdate(key, value) callback
     prop; the parent owns the staged map, dirty detection and rollback.
     Callers: feature-flags admin page through FlagRow; passes key, meta, the
     staged value (the raw text buffer for list[str]) and any per-field error. -->
<script lang="ts">
  import { t } from '$lib/i18n';

  let { key, meta, value, error, onupdate }: any = $props();

  const boolLabel = $derived(t('admin.flags.toggle', { key }));

  const objLabels = $derived([
    ['require_uppercase', t('admin.flags.requireUppercase')],
    ['require_lowercase', t('admin.flags.requireLowercase')],
    ['require_digit', t('admin.flags.requireDigit')],
    ['require_special_char', t('admin.flags.requireSpecialChar')]
  ]);

  function stageInt(raw: string): void {
    const n = Number(raw);
    if (raw === '' || Number.isNaN(n)) return;
    onupdate?.(key, n);
  }

  function stagePolicy(delta: Record<string, any>): void {
    onupdate?.(key, { ...value, ...delta });
  }
</script>

{#if meta.type === 'bool'}
  <label class="switch">
    <input type="checkbox" checked={value}
           onchange={(e) => onupdate?.(key, (e.currentTarget as HTMLInputElement).checked)}
           aria-label={boolLabel} />
    <span class="track"></span>
  </label>
{:else if meta.type === 'int'}
  <div class="field">
    <input class="ctl" type="number" inputmode="numeric" value={value} min={meta.min} max={meta.max}
           aria-label={key} aria-invalid={error ? 'true' : undefined}
           oninput={(e) => stageInt((e.currentTarget as HTMLInputElement).value)} />
  </div>
{:else if meta.type === 'str'}
  <div class="field">
    <input class="ctl" type="text" value={value} maxlength={meta.max_length} pattern="\S*"
           aria-label={key} aria-invalid={error ? 'true' : undefined}
           oninput={(e) => onupdate?.(key, (e.currentTarget as HTMLInputElement).value)} />
    {#if key === 'ai_local_model'}<span class="hint">{t('admin.flags.modelPatternHint')}</span>{/if}
  </div>
{:else if meta.type === 'list[str]'}
  <div class="field">
    <textarea class="ctl" rows={3} value={value} aria-label={key}
              oninput={(e) => onupdate?.(key, (e.currentTarget as HTMLTextAreaElement).value)}></textarea>
    <span class="hint">{t('admin.flags.corsOriginHint')}</span>
  </div>
{:else if meta.type === 'object'}
  <div class="object-group">
    <span class="og-label">{t('admin.flags.passwordPolicy')}</span>
    <label class="og-min">
      <span>{t('admin.flags.minLength')}</span>
      <input class="ctl" type="number" inputmode="numeric" min={6} max={32} value={value?.min_length}
             aria-label={t('admin.flags.minLength')} aria-invalid={error ? 'true' : undefined}
             oninput={(e) => stagePolicy({ min_length: Number((e.currentTarget as HTMLInputElement).value) })} />
    </label>
    <div class="og-toggles">
      {#each objLabels as [sub, label]}
        <div class="switch-row">
          <span>{label}</span>
          <label class="switch">
            <input type="checkbox" checked={value?.[sub]}
                   onchange={(e) => stagePolicy({ [sub]: (e.currentTarget as HTMLInputElement).checked })}
                   aria-label={label} />
            <span class="track"></span>
          </label>
        </div>
      {/each}
    </div>
  </div>
{/if}

<style>
  .field { margin-top: 0.5rem; max-width: 560px; }
  .ctl {
    width: 100%; font-family: var(--font-body); font-size: 0.95rem; color: var(--ink);
    background: var(--card); border: 1px solid var(--line-strong); border-radius: var(--radius);
    padding: 0.55rem 0.7rem; min-height: 40px; box-sizing: border-box;
  }
  textarea.ctl { resize: vertical; font-family: var(--font-mono, monospace); }
  .ctl:focus-visible { outline: none; border-color: var(--ring); box-shadow: 0 0 0 3px var(--focus-glow); }
  .ctl[aria-invalid='true'] { border-color: var(--danger); }
  .hint { display: block; color: var(--clay); font-size: 0.78rem; margin-top: 0.25rem; }

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
  .track::before { content: ''; position: absolute; inset-inline-start: 3px; top: 3px; width: 18px; height: 18px; background: var(--card); border-radius: 50%; transition: inset-inline-start 0.15s; }
  .switch input:checked + .track { background: var(--ochre); }
  .switch input:checked + .track::before { inset-inline-start: 23px; }
</style>