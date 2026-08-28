<!-- Path detail: step completion toggles, progress, and delete (force on 409). -->
<script lang="ts">
  import { browser } from '$app/environment';
  import { page } from '$app/stores';
  import { apiFetch, ApiError } from '$lib/api/client';
  import { query, invalidate } from '$lib/query';
  import { goto } from '$app/navigation';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Dialog from '$lib/components/ui/Dialog.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Icon from '$lib/icons/Icon.svelte';
  import ProgressMeter from '$lib/components/ProgressMeter.svelte';
  import { success, error as toastError, info } from '$lib/components/ui/toast';
  import TakeQuizDialog from '$lib/components/TakeQuizDialog.svelte';
  import QuizRunner from '$lib/components/QuizRunner.svelte';
  import { t } from '$lib/i18n';

  const id = $derived($page.params.id ?? '');
  let path = $state<any>(null);
  let loading = $state(true);
  let busyStep = $state<number | null>(null);
  let showDelete = $state(false);
  let dependents = $state<Record<string, number> | null>(null);
  let showQuiz = $state(false);
  let showQuizRunner = $state(false);
  let quizTest = $state<any>(null);
  let quizStep = $state<any>(null);
  let skills = $derived((path?.steps ?? []).map((s: any) => s.skill).filter((s: any) => s && s.id).map((s: any) => ({ id: s.id, name: s.name })));
  let progress = $derived(path?.steps && path.steps.length
    ? path.steps.filter((s: any) => s.is_completed).length / path.steps.length
    : 0);

  async function load() {
    loading = true;
    try { path = await query(['path', id], () => apiFetch('/paths/' + id)); }
    catch { path = null; }
    finally { loading = false; }
  }
  $effect(() => { id; load(); });

  $effect(() => {
    if (!browser) return;
    const onReady = (e: Event) => void onAiTestReady((e as CustomEvent).detail);
    const onFailed = (e: Event) =>
      toastError((e as CustomEvent).detail?.error ?? t('practiceTest.testFailed'));
    window.addEventListener('sse:ai_test_ready', onReady);
    window.addEventListener('sse:ai_test_failed', onFailed);
    return () => {
      window.removeEventListener('sse:ai_test_ready', onReady);
      window.removeEventListener('sse:ai_test_failed', onFailed);
    };
  });

  async function onAiTestReady(detail: any) {
    const { assessment_id: assessmentId, skill_id: skillId } = detail ?? {};
    if (!assessmentId || !skillId) return;
    try {
      const res = await apiFetch(`/assessments/${assessmentId}`);
      const mapped = (res?.questions ?? []).map((q: any) => ({
        id: q.id, text: q.text, options: q.options ?? [], topic: q.topic ?? q.skill,
      }));
      quizTest = { assessment_id: assessmentId, skill: { name: res?.skill ?? '' }, questions: mapped };
      quizStep = null;
      showQuizRunner = true;
    } catch (e) {
      toastError(e instanceof ApiError ? e.detail : t('common.error'));
    }
  }

  function handlePracticeTestStart(test: any) {
    quizTest = test;
    quizStep = null;
    showQuizRunner = true;
  }

  async function submitPracticeTest(assessmentId: number, answers: Record<number, number>) {
    const positional = quizTest?.questions.map((q: any) => answers[q.id] ?? -1) ?? [];
    const raw = await apiFetch('/assessments/submit', { method: 'POST', body: { assessment_id: assessmentId, answers: positional } });
    const responses = raw?.responses ?? [];
    const questions = quizTest?.questions ?? [];
    const correct = responses.filter((r: any) => r.is_correct).length;
    const graded = responses.map((r: any) => {
      const q = questions[r.question_index];
      let correctIndex = r.selected_index;
      if (q && r.correct_answer != null) {
        const idx = q.options.indexOf(r.correct_answer);
        if (idx >= 0) correctIndex = idx;
      }
      return { question_id: q ? q.id : r.question_index, correct_index: correctIndex, selected: r.selected_index, correct: r.is_correct };
    });
    return { passed: raw?.passed ?? true, score: (raw?.score ?? 100) / 100, correct, total: raw?.total_questions ?? responses.length, graded, weak_points: [], topics_to_master: [], resources: [] };
  }

  async function rateLevel(step: any, n: number) {
    if (!step.skill_id) return;
    const prev = step.current_level;
    busyStep = step.id;
    step.current_level = n;
    path = { ...path };
    try {
      await apiFetch(`/learning/skills/${step.skill_id}/proficiency`, {
        method: 'PUT', body: { level: n },
      });
      success(t('learn.ratingSaved'));
      await load();
    } catch (e) {
      step.current_level = prev;
      path = { ...path };
      toastError(e instanceof ApiError ? e.detail : t('learn.ratingFailed'));
    } finally {
      busyStep = null;
    }
  }

  async function toggle(step: any) {
    busyStep = step.id;
    try {
      if (step.is_completed) {
        await apiFetch(`/steps/${step.id}/undo-complete`, { method: 'POST' });
        step.is_completed = false;
        path = { ...path, progress };
        await invalidate(['dashboard']);
      } else if (step.skill) {
        await openStepQuiz(step);
      } else {
        await apiFetch(`/steps/${step.id}/complete`, { method: 'POST' });
        step.is_completed = true;
        path = { ...path, progress };
        await invalidate(['dashboard']);
      }
    } catch (e) {
      toastError(e instanceof ApiError ? e.detail : 'Update failed');
    } finally {
      busyStep = null;
    }
  }

  async function openStepQuiz(step: any) {
    busyStep = step.id;
    try {
      const test = await apiFetch(`/steps/${step.id}/test`, { method: 'POST' });
      quizTest = test;
      quizStep = step;
      showQuizRunner = true;
    } catch (e) {
      const noAssessment = e instanceof ApiError && e.status === 400 &&
        /no questions/i.test(String(e.detail));
      if (noAssessment) {
        await markStepComplete(step);
      } else {
        toastError(e instanceof ApiError ? e.detail : t('common.error'));
      }
    } finally {
      busyStep = null;
    }
  }

  async function markStepComplete(step: any) {
    await apiFetch(`/steps/${step.id}/complete`, { method: 'POST' });
    step.is_completed = true;
    path = { ...path, progress };
    await invalidate(['dashboard']);
    info(t('learn.noTest'));
  }

  async function submitStepTest(assessmentId: number, answers: Record<number, number>) {
    return await apiFetch(`/steps/${quizStep.id}/test/submit`, {
      method: 'POST',
      body: { assessment_id: assessmentId, answers },
    });
  }

  async function onQuizResult(res: any) {
    if (quizStep) {
      if (res?.passed) {
        quizStep.is_completed = true;
        path = { ...path, progress };
        invalidate(['dashboard']);
        success(t('learn.levelUp'));
      } else {
        info(t('learn.tryAgainLower'));
      }
    } else {
      info(t('practiceTest.testReady'));
      invalidate(['analyticsDashboard']);
      invalidate(['dashboard']);
    }
    try {
      await load();
    } catch {
      // best-effort refresh; ladder keeps its last known level on failure
    }
  }

  async function doDelete(force: boolean) {
    try {
      await apiFetch('/paths/' + id + (force ? '?force=true' : ''), { method: 'DELETE' });
      success('Path deleted');
      await invalidate(['paths']);
      goto('/learn');
    } catch (e) {
      if (e instanceof ApiError && e.status === 409 && e.dependents) {
        dependents = e.dependents;
        showDelete = true;
      } else {
        toastError(e instanceof ApiError ? e.detail : 'Delete failed');
      }
    }
  }
</script>

{#if loading}
  <div class="center-spin"><Spinner /></div>
{:else if !path}
  <Panel><p class="muted">{t('pathDetailPage.notFound')}</p></Panel>
{:else}
  <div class="head between">
    <div>
      <h1>{path.title}</h1>
      <Badge tone="accent">{path.goal_job_role ?? path.goal ?? ''}</Badge>
    </div>
    <Button variant="destructive" onclick={() => doDelete(false)}><Icon name="trash" size={16} />{t('pathDetailPage.deleteConfirm')}</Button>
    <Button onclick={() => (showQuiz = true)}><Icon name="sparkles" size={16} />{t('wizard.assessmentTitle')}</Button>
  </div>

  <div class="stats">
    <Panel title={t('pathDetailPage.progress')}><ProgressMeter value={progress * 100} /></Panel>
    <Panel title={t('pathDetailPage.duration')}><div class="big">{Math.round((path.steps ?? []).reduce((a: number, s: any) => a + (s.duration_hours ?? 0), 0))}h</div></Panel>
    <Panel title={t('pathDetailPage.skillsTitle')}><div class="big">{(path.steps ?? []).length}</div></Panel>
  </div>

  <h2 class="section-title">{t('pathDetailPage.stepsTitle')}</h2>
  <ol class="steps">
    {#each (path.steps ?? []).slice().sort((a: any, b: any) => (a.order_index ?? a.step_number ?? 0) - (b.order_index ?? b.step_number ?? 0)) as step}
      {@const stepLevel = step.current_level || step.selected_level || 1}
      <li class:done={step.is_completed}>
        <button class="toggle" onclick={() => toggle(step)} disabled={busyStep === step.id}>
          {#if busyStep === step.id}<Spinner />{:else if step.is_completed}<Icon name="check" size={16} />{:else}<Icon name="plus" size={16} />{/if}
        </button>
        <div class="body">
          <strong>{step.title}</strong>
          {#if step.content}<p class="muted">{step.content}</p>{/if}
          <div class="ladder" title={t('learn.levelLadder')}>
            <span class="ladder-label">{t('learn.level')}</span>
            <span class="ladder-dots">
              {#each [1, 2, 3, 4, 5] as n}
                <button class="dot" class:active={n === stepLevel} class:reached={n <= stepLevel}
                  title={`${t('learn.rateLevel')} — ${n}`} aria-label={`${t('learn.rateLevel')} ${n}`}
                  onclick={() => rateLevel(step, n)} disabled={busyStep === step.id}></button>
              {/each}
            </span>
            <span class="ladder-val">{stepLevel}</span>
          </div>
          <small class="muted">
            {step.duration_hours ?? 0}h
            {#if step.skill?.name} · {step.skill.name}{/if}
            {#if step.skill?.difficulty_level} · {t('pathDetailPage.skillLevel')}: {step.skill.difficulty_level}{/if}
            {#if step.current_topic} · {t('pathDetailPage.currentTopic')}: <strong>{step.current_topic}</strong>{/if}
          </small>
          {#if (step.learning_objectives ?? []).length}
            <ul class="obj">
              {#each step.learning_objectives as obj}<li>{obj}</li>{/each}
            </ul>
          {/if}
          {#if (step.resources ?? []).length}
            <div class="res">
              {#each step.resources as r}
                <a class="chip" href={r.url} target="_blank" rel="noopener noreferrer">{r.title}{#if r.type}<Badge tone="neutral">{r.type}</Badge>{/if}</a>
              {/each}
            </div>
          {/if}
        </div>
      </li>
    {/each}
  </ol>
{/if}

<Dialog bind:open={showDelete} title={t('pathDetailPage.deleteConfirm')}>
  <p>{t('pathDetailPage.deleteConfirm')}?</p>
  {#if dependents}
    <ul class="dep">
      {#each Object.entries(dependents) as [table, count]}<li>{count} × {table}</li>{/each}
    </ul>
  {/if}
  {#snippet footer()}
    <Button variant="ghost" onclick={() => (showDelete = false)}>{t('common.cancel')}</Button>
    <Button variant="destructive" onclick={() => doDelete(true)}>{t('common.forceDelete')}</Button>
  {/snippet}
</Dialog>

<TakeQuizDialog bind:open={showQuiz} {skills} onstart={handlePracticeTestStart} />

<QuizRunner
  bind:open={showQuizRunner}
  test={quizTest}
  objectives={quizStep?.learning_objectives ?? []}
  submit={quizStep ? submitStepTest : submitPracticeTest}
  onresult={onQuizResult}
  level={quizTest?.level ?? null}
  difficulty={quizTest?.difficulty ?? null}
/>

<style>
  .center-spin { display: flex; justify-content: center; padding: 3rem; }
  .head { margin-bottom: 1.2rem; flex-wrap: wrap; }
  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
  .big { font-family: var(--font-display); font-size: 1.8rem; color: var(--ochre-deep); }
  .section-title { margin-top: 2rem; font-size: 1.3rem; }
  .steps { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.6rem; }
  .steps li { display: flex; gap: 0.8rem; align-items: flex-start; padding: 0.8rem; border: 1px solid var(--line); border-radius: var(--radius); background: var(--paper); }
  .steps li.done { border-inline-start: 3px solid var(--sage); }
  .toggle { flex-shrink: 0; width: 32px; height: 32px; border-radius: 50%; border: 1px solid var(--line-strong); background: var(--paper-2); cursor: pointer; display: inline-flex; align-items: center; justify-content: center; color: var(--ochre-deep); }
  .toggle:disabled { opacity: 0.6; }
  .body { display: flex; flex-direction: column; gap: 0.2rem; }
  .obj { margin: 0.3rem 0 0; padding-inline-start: 1.1rem; color: var(--muted); font-size: 0.85rem; }
  .res { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.3rem; }
  .chip { display: inline-flex; align-items: center; gap: 0.35rem; text-decoration: none; font-size: 0.82rem; color: var(--accent-deep); border: 1px solid var(--line); border-radius: 999px; padding: 0.15rem 0.6rem; background: var(--paper-2); }
  .dep { margin: 0.5rem 0 0; padding-inline-start: 1.2rem; color: var(--danger); }
  .ladder { display: inline-flex; align-items: center; gap: 0.5rem; margin-top: 0.35rem; font-size: 0.8rem; color: var(--muted); }
  .ladder-label { font-weight: 600; color: var(--accent-deep); }
  .ladder-dots { display: inline-flex; gap: 0.25rem; }
  .dot { width: 10px; height: 10px; padding: 0; border-radius: 50%; border: 1px solid var(--line-strong); background: var(--paper-2); cursor: pointer; }
  .dot:disabled { opacity: 0.6; cursor: default; }
  .dot.reached { border-color: var(--sage); background: color-mix(in srgb, var(--sage) 30%, var(--paper)); }
  .dot.active { background: var(--accent-deep); border-color: var(--accent-deep); }
  .ladder-val { font-family: var(--font-display); color: var(--ochre-deep); font-weight: 600; }
</style>
