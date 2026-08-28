<script lang="ts">
  import Panel from '$lib/components/ui/Panel.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import { t } from '$lib/i18n';

  interface Props {
    field: string;
    goal: string;
    roleSkills: string[];
    overall: number;
    weeklyHours: number;
    format: string;
    language: string;
    isFree: boolean;
    analysis: any;
    analysisError: string;
  }

  let {
    field, goal, roleSkills, overall, weeklyHours,
    format, language, isFree, analysis, analysisError
  }: Props = $props();
</script>

<Panel>
  <div class="review">
    <div><span class="muted">{t('wizard.summaryField')}</span><strong>{field || '—'}</strong></div>
    <div><span class="muted">{t('wizard.summaryGoal')}</span><strong>{goal || '—'}</strong></div>
    <div><span class="muted">{t('wizard.summaryLevel')}</span><strong>{roleSkills.length ? roleSkills.length + ' ' + t('wizard.levelTitle') : overall}</strong></div>
    <div><span class="muted">{t('wizard.summaryHours')}</span><strong>{weeklyHours}h</strong></div>
    <div><span class="muted">{t('wizard.summaryFormat')}</span><strong>{format}</strong></div>
    <div><span class="muted">{t('wizard.summaryLanguage')}</span><strong>{language}</strong></div>
    <div><span class="muted">{t('wizard.summaryFreeContent')}</span><strong>{isFree ? t('wizard.summaryYes') : t('wizard.summaryNo')}</strong></div>
  </div>

  <div class="analysis">
    <h3>{t('wizard.analysisTitle')}</h3>
    {#if analysisError}
      <p class="muted">{analysisError}</p>
    {:else if analysis}
      {#if analysis.recommended_focus?.length}
        <div class="a-block"><span class="muted">{t('wizard.recommendedFocus')}</span>
          <div class="chips">{#each analysis.recommended_focus as f}<span class="chip">{f}</span>{/each}</div>
        </div>
      {/if}
      {#if analysis.estimated_weeks != null}
        <div class="a-block"><span class="muted">{t('wizard.estimatedWeeks')}</span><strong>{analysis.estimated_weeks}</strong></div>
      {/if}
      {#if analysis.strengths?.length}
        <div class="a-block"><span class="muted">{t('wizard.strengths')}</span>
          <div class="chips">{#each analysis.strengths as s}<span class="chip ok">{s}</span>{/each}</div>
        </div>
      {/if}
      {#if analysis.weaknesses?.length}
        <div class="a-block"><span class="muted">{t('wizard.weaknesses')}</span>
          <div class="chips">{#each analysis.weaknesses as w}<span class="chip warn">{w}</span>{/each}</div>
        </div>
      {/if}
      {#if analysis.per_skill?.length}
        <div class="a-block">
          <span class="muted">{t('wizard.placementTitle')}</span>
          <ul class="placement">
            {#each analysis.per_skill as ps}
              <li>
                <span class="p-name">{ps.skill}</span>
                <span class="p-level">{t('wizard.placementLevel')}: <strong>{ps.assessed_level}</strong></span>
                {#if ps.weakness}<span class="p-weak">{ps.weakness}</span>{/if}
              </li>
            {/each}
          </ul>
        </div>
      {/if}
    {:else}
      <div class="center-spin"><Spinner /></div>
    {/if}
  </div>
</Panel>

<style>
  .review { display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; }
  .review .muted { display: block; font-size: 0.8rem; }
  .analysis { margin-top: 1.2rem; border-top: 1px solid var(--line); padding-top: 1rem; }
  .analysis h3 { margin: 0 0 0.6rem; font-size: 1rem; }
  .a-block { margin-bottom: 0.7rem; }
  .a-block .muted { display: block; font-size: 0.8rem; margin-bottom: 0.3rem; }
  .chips { display: flex; flex-wrap: wrap; gap: 0.4rem; }
  .chip { background: var(--accent-soft); color: var(--accent-deep); border-radius: 999px; padding: 0.2rem 0.7rem; font-size: 0.82rem; }
  .chip.ok { background: color-mix(in srgb, #16a34a 18%, var(--paper)); color: #15803d; }
  .chip.warn { background: color-mix(in srgb, #d97706 18%, var(--paper)); color: #b45309; }
  .placement { list-style: none; margin: 0.2rem 0 0; padding: 0; display: flex; flex-direction: column; gap: 0.35rem; }
  .placement li { display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem; font-size: 0.85rem; }
  .p-name { font-weight: 600; color: var(--ink); }
  .p-level { color: var(--accent-deep); }
  .p-weak { color: var(--muted); font-style: italic; }
  .center-spin { display: flex; justify-content: center; padding: 1.2rem; }
</style>
