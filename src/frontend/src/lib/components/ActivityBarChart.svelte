<!-- This-week activity bar chart. Plain CSS bars (RTL-safe via flex flow),
     day labels localized. Empty state via i18n when no activity exists. -->
<script lang="ts">
  import { t } from '$lib/i18n';
  import { i18n } from '$lib/i18n';

  let { data = [] }: { data?: { date: string; count: number }[] } = $props();

  const CHART_H = 130;
  const max = $derived(Math.max(1, ...data.map((d) => d.count)));

  function shortDay(iso: string): string {
    const d = new Date(iso + 'T00:00:00');
    return d.toLocaleDateString(i18n.locale === 'ar' ? 'ar-EG' : 'en-US', { weekday: 'short' });
  }
</script>

{#if data.length === 0}
  <p class="muted empty">{t('analyticsPage.noActivity')}</p>
{:else}
  <div class="chart">
    {#each data as d (d.date)}
      <div class="col">
        <div class="track" style="height: {CHART_H}px">
          {#if d.count > 0}
            <div class="bar" style="height: {(d.count / max) * CHART_H}px"></div>
          {/if}
        </div>
        <span class="lbl">{shortDay(d.date)}</span>
      </div>
    {/each}
  </div>
{/if}

<style>
  .empty { padding: 1rem 0; }
  .chart { display: flex; gap: 0.6rem; align-items: flex-end; }
  .col { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 0.4rem; min-width: 0; }
  .track { width: 100%; max-width: 42px; display: flex; align-items: flex-end; justify-content: center;
    background: var(--paper-2); border: 1px solid var(--line); border-radius: var(--radius); }
  .bar { width: 100%; background: var(--accent-deep); border-radius: var(--radius); transition: height 0.4s ease; }
  .lbl { font-size: 0.7rem; color: var(--muted); white-space: nowrap; }
</style>
