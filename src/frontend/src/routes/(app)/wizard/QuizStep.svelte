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

  /**
   * Handles the SSE event announcing that the AI quiz is ready, storing the
   * streamed questions when the job id matches the one this component requested.
   */
  function onQuizReady(e: CustomEvent) {
    if (quizJobId && e.detail?.job_id === quizJobId) {
      quizQuestions = e.detail?.questions ?? [];
      quizStatus = quizQuestions.length ? 'ready' : 'error';
      if (!quizQuestions.length) quizError = t('wizard.noQuestions');
    }
  }

  /**
   * Handles the SSE event reporting that the AI quiz failed, surfacing the
   * backend error when the failing job id matches the one this component requested.
   */
  function onQuizFailed(e: CustomEvent) {
    if (quizJobId && e.detail?.job_id === quizJobId) {
      quizStatus = 'error';
      quizError = e.detail?.error || t('wizard.quizError');
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
   * Requests a placement quiz job from the backend for the selected goal and
   * records the returned job id so later SSE events can be correlated.
   */
  async function startQuiz() {
    if (!goal) return;
    quizStatus = 'requesting';
    quizError = '';
    try {
      const r = await apiFetch('/ai/wizard-quiz', {
        method: 'POST', body: { goal }
      });
      quizJobId = r.job_id;
    } catch (e) {
      quizStatus = 'error';
      quizError = e instanceof ApiError ? e.detail : t('wizard.quizError');
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

{#if aiEnabled && quizMode === null}
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
  .link { background: none; border: none; color: var(--accent-deep); cursor: pointer; font-family: var(--font-body); font-size: 0.9rem; text-decoration: underline; padding: 0.4rem 0; }
  .link:focus-visible { outline: none; box-shadow: 0 0 0 3px var(--focus-glow); border-radius: var(--radius); }
  .q { border: 1px solid var(--line); border-radius: var(--radius); padding: 0.8rem; margin-bottom: 0.8rem; }
  .q-text { font-weight: 500; margin: 0 0 0.5rem; color: var(--ink); }
  .q-opts { display: grid; gap: 0.4rem; }
  .q-opt { display: flex; align-items: center; gap: 0.5rem; color: var(--ink-soft); cursor: pointer; }
  .q-opt input { width: 18px; height: 18px; accent-color: var(--accent); }
</style>
