<!-- Interactive step-test runner: MCQs, prioritized results, study guidance.
     Given a `test` payload + a `submit` callback, renders questions, grades on
     submit, then shows score, per-question correctness, weak points / topics
     to master and resources. Optional AI rationale via /api/ai/explain. -->
<script lang="ts">
  import { apiFetch, ApiError } from '$lib/api/client';
  import Button from '$lib/components/ui/Button.svelte';
  import Dialog from '$lib/components/ui/Dialog.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import { t } from '$lib/i18n';

  let {
    open = $bindable(false),
    test = null,
    objectives = [],
    submit = async (_assessmentId: number, _answers: Record<number, number>) => ({}),
    onresult = (_r: any) => {},
    onclose = () => {},
    level = null as number | null,
    difficulty = null as number | null,
    diagnostic = null as any,
  }: any = $props();

  let selected = $state<Record<number, number>>({});
  let result = $state<any>(null);
  let busy = $state(false);
  let error = $state('');
  let explaining = $state(false);
  let explain = $state<Record<number, string>>({});
  let advice = $state('');

  $effect(() => {
    if (open) {
      selected = {};
      result = null;
      busy = false;
      error = '';
      explaining = false;
      explain = {};
      advice = '';
    }
  });

  $effect(() => {
    if (diagnostic && result) {
      if (Array.isArray(diagnostic.weak_points)) result.weak_points = diagnostic.weak_points;
      if (Array.isArray(diagnostic.topics_to_master)) result.topics_to_master = diagnostic.topics_to_master;
    }
  });

  let answeredCount = $derived(
    test ? test.questions.filter((q: any) => selected[q.id] !== undefined).length : 0
  );

  function gradedFor(qid: number) {
    if (!result) return null;
    return (result.graded || []).find((g: any) => g.question_id === qid) || null;
  }

  async function doSubmit() {
    if (!test) return;
    busy = true;
    error = '';
    try {
      const res = await submit(test.assessment_id, selected);
      result = res;
      onresult(res);
    } catch (e) {
      error = e instanceof ApiError ? e.detail : t('common.error');
    } finally {
      busy = false;
    }
  }

  async function doExplain() {
    if (!test) return;
    explaining = true;
    advice = '';
    explain = {};
    try {
      const positional = test.questions.map((q: any) => selected[q.id] ?? -1);
      const data = await apiFetch('/ai/explain', {
        method: 'POST',
        body: { assessment_id: test.assessment_id, answers: positional },
      });
      const map: Record<number, string> = {};
      for (const e of data.explanations || []) {
        const q = test.questions[e.question_index];
        if (q) map[q.id] = e.why;
      }
      explain = map;
      advice = data.advice || '';
    } catch {
      advice = t('stepTest.explainUnavailable');
    } finally {
      explaining = false;
    }
  }

  function retry() {
    selected = {};
    result = null;
    explain = {};
    advice = '';
  }

  function close() {
    open = false;
    onclose();
  }
</script>

<Dialog bind:open title={test ? `${t('stepTest.title')}: ${test.skill?.name ?? ''}` : t('stepTest.title')} {onclose}>
  {#if test}
    <div class="stack">
      <p class="muted">{t('stepTest.intro')}</p>
      {#if level}
        <p class="level-note">
          {t('learn.testAtLevel', { level })}
          {#if difficulty}<span class="tag">{t('learn.level')} {level} · {t('pathDetailPage.skillLevel')}: {difficulty}</span>{/if}
        </p>
      {/if}

      {#if !result}
        {#each test.questions as q, qi}
          <fieldset class="q">
            <legend>{t('stepTest.questionOf', { n: qi + 1 })}</legend>
            <p class="qtext">{q.text}</p>
            {#if q.topic}<span class="tag">{q.topic}</span>{/if}
            <div class="opts">
              {#each q.options as opt, oi}
                <label class="opt" class:sel={selected[q.id] === oi}>
                  <input type="radio" name={`q${q.id}`} value={oi}
                         checked={selected[q.id] === oi}
                         onchange={() => (selected[q.id] = oi)} />
                  <span>{opt}</span>
                </label>
              {/each}
            </div>
          </fieldset>
        {/each}

        {#if error}<p class="err">{error}</p>{/if}
        <p class="muted small">{t('stepTest.answered', { n: answeredCount, total: test.questions.length })}</p>
      {:else}
        <div class="banner" class:pass={result.passed} class:fail={!result.passed}>
          <strong>{result.passed ? t('stepTest.passed') : t('stepTest.failed')}</strong>
          <span>{t('stepTest.score')}: {Math.round(result.score * 100)}%
            ({result.correct}/{result.total})</span>
        </div>

        {#each test.questions as q, qi}
          {@const g = gradedFor(q.id)}
          <div class="q">
            <p class="qtext">
              {t('stepTest.questionOf', { n: qi + 1 })}. {q.text}
            </p>
            <ul class="opts review">
              {#each q.options as opt, oi}
                <li class:correct={g && oi === g.correct_index}
                    class:wrong={g && !g.correct && oi === g.selected}>
                  {opt}
                  {#if g && oi === g.correct_index}<span class="pill ok">✓</span>{/if}
                  {#if g && !g.correct && oi === g.selected}<span class="pill bad">✗</span>{/if}
                </li>
              {/each}
            </ul>
            {#if explain[q.id]}<p class="why">{explain[q.id]}</p>{/if}
          </div>
        {/each}

        <div class="panels">
          <div class="panel">
            <h4>{t('stepTest.weakPoints')}</h4>
            {#if (result.weak_points || []).length}
              <ul>{#each result.weak_points as w}<li>{w}</li>{/each}</ul>
            {:else}
              <p class="muted small">{t('stepTest.allCorrect')}</p>
            {/if}
          </div>
          <div class="panel">
            <h4>{t('stepTest.topicsToMaster')}</h4>
            {#if (result.topics_to_master || []).length}
              <ul>{#each result.topics_to_master as w}<li>{w}</li>{/each}</ul>
            {/if}
          </div>
        </div>

        {#if (objectives || []).length}
          <div class="panel">
            <h4>{t('stepTest.objectives')}</h4>
            <ul>{#each objectives as o}<li>{o}</li>{/each}</ul>
          </div>
        {/if}

        {#if (result.resources || []).length}
          <div class="panel">
            <h4>{t('stepTest.resources')}</h4>
            <div class="res">
              {#each result.resources as r}
                <a class="chip" href={r.url} target="_blank" rel="noopener noreferrer">{r.title}{#if r.type}<span class="pill">{r.type}</span>{/if}</a>
              {/each}
            </div>
          </div>
        {/if}

        {#if advice}<p class="why">{advice}</p>{/if}
        <div class="actions">
          <Button variant="ghost" onclick={doExplain} disabled={explaining}>
            {#if explaining}<Spinner />{:else}{t('stepTest.explain')}{/if}
          </Button>
        </div>
      {/if}
    </div>
  {/if}

  {#snippet footer()}
    {#if !result}
      <Button variant="ghost" onclick={close}>{t('common.cancel')}</Button>
      <Button onclick={doSubmit} disabled={busy || answeredCount === 0}>
        {#if busy}<Spinner />{:else}{t('stepTest.submit')}{/if}
      </Button>
    {:else}
      {#if !result.passed}
        <Button variant="ghost" onclick={retry}>{t('stepTest.retry')}</Button>
      {/if}
      <Button onclick={close}>{t('stepTest.close')}</Button>
    {/if}
  {/snippet}
</Dialog>

<style>
  .stack { display: flex; flex-direction: column; gap: 1rem; }
  .level-note { font-size: 0.85rem; color: var(--ochre-deep); }
  .level-note .tag { margin-inline-start: 0.4rem; }
  .muted { color: var(--clay); }
  .small { font-size: 0.82rem; }
  .q { border: 1px solid var(--line); border-radius: var(--radius); padding: 0.8rem; margin: 0; }
  .qtext { font-weight: 600; margin: 0.2rem 0 0.5rem; }
  .tag { display: inline-block; font-size: 0.72rem; color: var(--ochre-deep); border: 1px solid var(--line); border-radius: 999px; padding: 0.05rem 0.5rem; }
  .opts { display: flex; flex-direction: column; gap: 0.35rem; }
  .opts.review { list-style: none; padding: 0; margin: 0.3rem 0 0; }
  .opt { display: flex; align-items: center; gap: 0.5rem; padding: 0.35rem 0.5rem; border: 1px solid var(--line); border-radius: var(--radius); cursor: pointer; }
  .opt.sel { border-color: var(--ochre-deep); background: var(--paper-2); }
  .opts.review li { padding: 0.3rem 0.5rem; border-radius: var(--radius); border: 1px solid var(--line); }
  .opts.review li.correct { border-color: var(--sage); background: color-mix(in srgb, var(--sage) 14%, var(--card)); }
  .opts.review li.wrong { border-color: var(--danger); background: color-mix(in srgb, var(--danger) 12%, var(--card)); }
  .pill { font-size: 0.7rem; margin-inline-start: 0.4rem; padding: 0 0.35rem; border-radius: 999px; }
  .pill.ok { color: var(--sage); }
  .pill.bad { color: var(--danger); }
  .banner { display: flex; flex-direction: column; gap: 0.2rem; padding: 0.7rem 0.9rem; border-radius: var(--radius); }
  .banner.pass { border: 1px solid var(--sage); background: color-mix(in srgb, var(--sage) 12%, var(--card)); }
  .banner.fail { border: 1px solid var(--danger); background: color-mix(in srgb, var(--danger) 10%, var(--card)); }
  .panels { display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; }
  .panel { border: 1px solid var(--line); border-radius: var(--radius); padding: 0.7rem; }
  .panel h4 { margin: 0 0 0.4rem; font-size: 0.9rem; }
  .panel ul { margin: 0; padding-inline-start: 1.1rem; }
  .why { font-size: 0.85rem; color: var(--clay); border-inline-start: 3px solid var(--line-strong); padding-inline-start: 0.6rem; }
  .res { display: flex; flex-wrap: wrap; gap: 0.4rem; }
  .chip { display: inline-flex; align-items: center; gap: 0.35rem; text-decoration: none; font-size: 0.82rem; color: var(--ochre-deep); border: 1px solid var(--line); border-radius: 999px; padding: 0.15rem 0.6rem; background: var(--paper-2); }
  .actions { display: flex; justify-content: flex-end; }
  .err { color: var(--danger); }
</style>
