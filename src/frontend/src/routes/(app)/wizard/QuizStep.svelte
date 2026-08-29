<script lang="ts">
  import { apiFetch, ApiError } from '$lib/api/client';
  import { onMount, onDestroy } from 'svelte';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Icon from '$lib/icons/Icon.svelte';
  import { t } from '$lib/i18n';

  interface Props {
    aiEnabled: boolean | null;
    goal: string;
    weeklyHours: number;
    quizMode: 'quiz' | 'self' | null;
    answers: Record<string, number>;
    roleSkills: string[];
    analysis: any;
    onComplete: () => void;
  }

  let {
    aiEnabled, goal, weeklyHours,
    quizMode = $bindable(), answers = $bindable(),
    roleSkills = $bindable(), analysis = $bindable(),
    onComplete
  }: Props = $props();

  let quizJobId = $state<string | null>(null);
  let quizQuestions = $state<any[]>([]);
  let quizAnswers = $state<Record<string, number>>({});
  let quizStatus = $state<'idle' | 'requesting' | 'ready' | 'submitting' | 'error'>('idle');
  let quizError = $state('');
  let enriching = $state(false);

  /**
   * Handles the SSE event announcing enrichment questions, upserting each
   * streamed question by id over the bank version already on screen; the final
   * more:false closes the job and clears the enriching indicator.
   */
  function onQuizReady(e: CustomEvent) {
    if (!quizJobId || e.detail?.job_id !== quizJobId) return;
    const more = e.detail?.more !== false;
    const incoming: any[] = e.detail?.questions ?? [];
    if (incoming.length) {
      const byId = new Map(quizQuestions.map((q: any) => [q.id, q]));
      for (const q of incoming) byId.set(q.id, q);
      quizQuestions = Array.from(byId.values());
      quizStatus = 'ready';
    }
    if (!more) {
      enriching = false;
      quizStatus = 'ready';
    }
  }

  /**
   * Handles the SSE event reporting that the AI quiz failed; the seeded-bank
   * quiz stays usable, so this only stops the enriching indicator for the
   * failing job id the component requested.
   */
  function onQuizFailed(e: CustomEvent) {
    if (quizJobId && e.detail?.job_id === quizJobId) {
      enriching = false;
      quizStatus = 'ready';
    }
  }

  onMount(() => {
    window.addEventListener('sse:ai_quiz_ready', onQuizReady as EventListener);
    window.addEventListener('sse:ai_quiz_failed', onQuizFailed as EventListener);
  });

  onDestroy(() => {
    window.removeEventListener('sse:ai_quiz_ready', onQuizReady as EventListener);
    window.removeEventListener('sse:ai_quiz_failed', onQuizFailed as EventListener);
  });

  /**
   * Requests the placement quiz from the seeded question bank and renders it
   * immediately from the synchronous response, keeping the returned job id so
   * later SSE enrichment events can be correlated to this request.
   */
  async function startQuiz() {
    if (!goal) return;
    quizStatus = 'requesting';
    quizError = '';
    try {
      const r = await apiFetch('/ai/wizard-quiz', {
        method: 'POST', body: { goal }
      });
      quizQuestions = r.questions ?? [];
      quizJobId = r.job_id;
      quizStatus = 'ready';
      quizMode = 'quiz';
      quizError = '';
    } catch (e) {
      quizStatus = 'error';
      quizError = e instanceof ApiError ? e.detail : t('wizard.quizError');
    }
  }

  /**
   * Kicks off an optional AI enrichment job for the already-shown bank quiz,
   * leaving the synchronous questions on screen; improved question deltas arrive
   * non-blocking via onQuizReady and the whole upgrade stays soft-failing.
   */
  async function enrichQuiz() {
    if (!goal || enriching) return;
    enriching = true;
    try {
      const r = await apiFetch('/ai/wizard-quiz', {
        method: 'POST', body: { goal, enrich: true }
      });
      quizJobId = r.job_id;
    } catch (e) {
      enriching = false;
    }
  }

  /**
   * Submits the collected quiz answers for analysis, then writes the resulting
   * per-skill assessment back into the shared wizard state and advances to the
   * next step via the supplied completion callback.
   */
  async function submitQuiz() {
    if (!quizJobId) return;
    quizStatus = 'submitting';
    try {
      const r = await apiFetch('/wizard/analysis', {
        method: 'POST',
        body: {
          goal, weekly_hours: weeklyHours,
          quiz_job_id: quizJobId, answers: quizAnswers
        }
      });
      analysis = r;
      answers = Object.fromEntries(
        (r.per_skill ?? []).map((ps: any) => [ps.skill, ps.assessed_level]));
      roleSkills = (r.per_skill ?? []).map((ps: any) => ps.skill);
      onComplete();
    } catch (e) {
      quizStatus = 'error';
      quizError = e instanceof ApiError ? e.detail : t('wizard.quizError');
    }
  }
</script>

{#if quizMode === null}
  <p class="sub">{t('wizard.placementQuizDesc')}</p>
  <div class="quiz-choice">
    <Button onclick={startQuiz} disabled={quizStatus === 'requesting'}>
      {#if quizStatus === 'requesting'}<Spinner />{:else}<Icon name="sparkles" size={16} />{/if}
      {quizStatus === 'requesting' ? t('wizard.generating') : t('wizard.takePlacementQuiz')}
    </Button>
    <button class="link" onclick={() => (quizMode = 'self')}>{t('wizard.useSelfAssessment')}</button>
  </div>
{:else if quizMode === 'quiz'}
  <p class="sub">{t('wizard.placementQuizTitle')}</p>
  {#if quizStatus === 'requesting'}
    <div class="center-spin"><Spinner /></div>
  {:else if quizStatus === 'error'}
    <p class="err-state"><Icon name="alert" size={18} /> {quizError || t('wizard.quizError')}</p>
    <button class="link" onclick={() => (quizMode = 'self')}>{t('wizard.useSelfAssessment')}</button>
  {:else if quizStatus === 'ready' || quizStatus === 'submitting'}
    {#if aiEnabled && quizStatus === 'ready'}
      <div class="enrich-row">
        {#if enriching}
          <span class="enriching"><Spinner /> {t('wizard.enriching')}</span>
        {:else}
          <Button variant="ghost" size="sm" onclick={enrichQuiz}>
            <Icon name="sparkles" size={14} /> {t('wizard.enrichQuiz')}
          </Button>
        {/if}
      </div>
    {/if}
    {#each quizQuestions as q, i}
      <div class="q">
        <p class="q-text">{t('wizard.questionLabel', { n: i + 1 })}: {q.text}</p>
        <div class="q-opts">
          {#each q.options as opt, oi}
            <label class="q-opt">
              <input type="radio" name={q.id} value={oi}
                checked={quizAnswers[q.id] === oi}
                onchange={() => (quizAnswers[q.id] = oi)} />
              <span>{opt}</span>
            </label>
          {/each}
        </div>
      </div>
    {/each}
    {#if quizStatus === 'submitting'}
      <div class="center-spin"><Spinner /></div>
    {:else}
      <Button onclick={submitQuiz}>{t('wizard.submitQuiz')}</Button>
    {/if}
  {/if}
{/if}

<style>
  .sub { margin: 0 0 0.8rem; color: var(--ink-soft); }
  .err-state { display: flex; align-items: center; gap: 0.5rem; color: var(--danger); margin-top: 0.8rem; }
  .center-spin { display: flex; justify-content: center; padding: 1.2rem; }
  .quiz-choice { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; margin-top: 0.4rem; }
  .enrich-row { display: flex; justify-content: flex-end; margin-bottom: 0.6rem; }
  .enriching { display: inline-flex; align-items: center; gap: 0.5rem; color: var(--ink-soft); font-size: 0.9rem; }
  .link { background: none; border: none; color: var(--ochre-deep); cursor: pointer; font-family: var(--font-body); font-size: 0.9rem; text-decoration: underline; padding: 0.4rem 0; }
  .link:focus-visible { outline: none; box-shadow: 0 0 0 3px var(--focus-glow); border-radius: var(--radius); }
  .q { border: 1px solid var(--line); border-radius: var(--radius); padding: 0.8rem; margin-bottom: 0.8rem; }
  .q-text { font-weight: 500; margin: 0 0 0.5rem; color: var(--ink); }
  .q-opts { display: grid; gap: 0.4rem; }
  .q-opt { display: flex; align-items: center; gap: 0.5rem; color: var(--ink-soft); cursor: pointer; }
  .q-opt input { width: 18px; height: 18px; accent-color: var(--ochre); }
</style>
