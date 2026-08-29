<!-- Presentational KPI card. All visible strings are caller-supplied via the
     label / value / hint props — the caller owns localization with t(), so
     this component never calls t() itself and assumes nothing about locale.
     Accents only the LTR/RTL-safe layout; flat panel per design system. -->
<script lang="ts">
  import Icon from '$lib/icons/Icon.svelte';

  let {
    label,
    value,
    hint,
    icon,
    muted = false
  }: {
    label: string;
    value: string | number;
    hint?: string;
    icon?: string;
    muted?: boolean;
  } = $props();
</script>

<div class="card" class:muted>
  <div class="top">
    {#if icon}
      <span class="ic"><Icon name={icon} size={16} /></span>
    {/if}
    <span class="label">{label}</span>
  </div>
  <div class="value">{value}</div>
  {#if hint}
    <div class="hint">{hint}</div>
  {/if}
</div>

<style>
  .card {
    background: var(--card); border: 1px solid var(--line); border-radius: var(--radius-lg);
    padding: 1.1rem 1.2rem; display: flex; flex-direction: column; gap: 0.35rem;
    font-family: var(--font-body); color: var(--ink); min-width: 0;
  }
  .card.muted { opacity: 0.6; }
  .top { display: flex; align-items: center; gap: 0.45rem; }
  .ic { color: var(--ochre-deep); display: inline-flex; align-items: center; }
  .label { font-size: 0.8rem; color: var(--clay); }
  .value { font-size: 1.9rem; font-weight: 800; line-height: 1.1; color: var(--ink); letter-spacing: -0.02em; }
  .hint { font-size: 0.75rem; color: var(--clay); }
</style>
