<!-- FlagRow: schema-driven feature-flag row shell. Renders the key + type
     label, the read-only/restart/live badge (metadata precedence), an optional
     description, the per-type control via the children snippet, and the inline
     per-field error line. Read-only flags render their display value instead.
     Callers: feature-flags admin page; passes key, the FLAG_SCHEMA meta entry,
     the staged value and any per-field error. -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import { t } from '$lib/i18n';

  let { key, meta, value, error, description, children }: any = $props();

  const badge = $derived(
    !meta.editable
      ? { label: t('admin.flags.readOnlyBadge'), tone: 'neutral' }
      : meta.restart
        ? { label: t('admin.flags.appliesAfterRestart'), tone: 'warn' }
        : meta.live
          ? { label: t('admin.flags.live'), tone: 'ok' }
          : null
  );

  const typeLabel = $derived(
    meta.type === 'bool'
      ? t('admin.flags.typeBool')
      : meta.type === 'int'
        ? t('admin.flags.typeInt')
        : meta.type === 'str'
          ? t('admin.flags.typeStr')
          : meta.type === 'list[str]'
            ? t('admin.flags.typeListStr')
            : t('admin.flags.typeObject')
  );

  const displayValue = $derived(
    meta.type === 'bool'
      ? value
        ? t('admin.flags.on')
        : t('admin.flags.off')
      : Array.isArray(value)
        ? value.join(', ')
        : value && typeof value === 'object'
          ? JSON.stringify(value)
          : String(value ?? '')
  );
</script>

<div class="flag {!meta.editable ? 'readonly' : ''}">
  <div class="head">
    <div class="label">
      <span class="k">{key}</span>
      <span class="type">{typeLabel}</span>
    </div>
    {#if badge}<Badge tone={badge.tone}>{badge.label}</Badge>{/if}
  </div>

  {#if !meta.editable}
    <div class="value">{displayValue}</div>
  {:else}
    {#if description}<p class="desc">{description}</p>{/if}
    {@render children()}
    {#if error}<span class="err" role="alert">{error}</span>{/if}
  {/if}
</div>

<style>
  .flag { padding: 0.8rem 0; border-bottom: 1px dashed var(--line); }
  .flag.readonly { opacity: 0.85; }
  .head { display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
  .label { display: flex; flex-direction: column; gap: 0.15rem; }
  .k { font-weight: 600; color: var(--ink); }
  .type { font-size: 0.75rem; color: var(--clay); }
  .value { margin-top: 0.4rem; font-size: 0.85rem; color: var(--ink-soft); word-break: break-word; }
  .desc { margin: 0.4rem 0 0; font-size: 0.82rem; color: var(--clay); }
  .err { display: block; color: var(--danger); font-size: 0.78rem; margin-top: 0.3rem; }
</style>