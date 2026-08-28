<!-- Path-generation wizard. Five steps: field, role, level, preferences, summary.
     Implements the two-phase contract: a read-only /api/wizard/analysis call
     precedes /api/generate-path/ so the created path is personalized. -->
<script lang="ts">
  import { apiFetch, ApiError } from '$lib/api/client';
  import { query } from '$lib/query';
  import { goto } from '$app/navigation';
  import { onMount, onDestroy } from 'svelte';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Icon from '$lib/icons/Icon.svelte';
  import { error as toastError, success } from '$lib/components/ui/toast';
  import { t } from '$lib/i18n';

  const totalSteps = 5;

  let options = $state<any>(null);
  let step = $state(0);

  // Step 1 — field
  let field = $state('');
  // Step 2 — role
  let goal = $state('');
  let search = $state('');
  // Step 3 — level self-assessment: skill name -> level (0-5)
  let answers = $state<Record<string, number>>({});
  let roleSkills = $state<string[]>([]);
  let skillsLoading = $state(false);
  let skillsError = $state('');
  let overall = $state(0);
  // Step 4 — preferences
  let weeklyHours = $state(10);
  let isFree = $state(true);
  let format = $state('any');
  let language = $state('en');
  // Step 5 — summary + analysis
  let analysis = $state<any>(null);
  let analysisError = $state('');

  // AI placement quiz flow (alternative to self-assessment when AI enabled)
  let aiEnabled = $state<boolean | null>(null);
  let quizMode = $state<'quiz' | 'self' | null>(null);
  let quizJobId = $state<string | null>(null);
  let quizQuestions = $state<any[]>([]);
  let quizAnswers = $state<Record<string, number>>({});
  let quizStatus = $state<'idle' | 'requesting' | 'ready' | 'submitting' | 'error'>('idle');
  let quizError = $state('');

  let generating = $state(false);
  let optionsLoading = $state(true);
  let optionsError = $state('');

  let steps = $derived([
    t('wizard.step1Title'), t('wizard.step2Title'), t('wizard.step3Title'),
    t('wizard.step4Title'), t('wizard.step5Title')
  ]);

  $effect(() => {
    optionsLoading = true;
    optionsError = '';
    query(['wizardOptions'], () => apiFetch('/wizard-options'))
      .then((d) => (options = d))
      .catch((e) => { optionsError = e?.detail || t('wizard.optionsLoadError'); })
      .finally(() => (optionsLoading = false));
  });

  $effect(() => {
    apiFetch('/ai/status')
      .then((d) => {
        aiEnabled = !!(d && d.ai_enabled);
        if (!aiEnabled) quizMode = 'self';
      })
      .catch(() => { aiEnabled = false; quizMode = 'self'; });
  });

  function onQuizReady(e: CustomEvent) {
    if (quizJobId && e.detail?.job_id === quizJobId) {
      quizQuestions = e.detail?.questions ?? [];
      quizStatus = quizQuestions.length ? 'ready' : 'error';
      if (!quizQuestions.length) quizError = t('wizard.noQuestions');
    }
  }

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

  let fields = $derived(!options ? [] : Object.keys(options.career_fields ?? {}));
  let rolesForField = $derived(
    !options ? [] : (field ? (options.career_fields?.[field] ?? []) : (options.job_roles ?? []))
  );
  let roles = $derived(
    rolesForField.filter((r: any) =>
      !search || r.title.toLowerCase().includes(search.toLowerCase()))
  );
  // Answers payload is always { skillName: integerLevel (0-5) }, matching the
  // backend contract. When no role skills exist the map is empty ({}).
  let submitAnswers = $derived(answers);
  let stepValid = $derived(
    step === 0 ? !!field :
    step === 1 ? !!goal :
    true
  );

  async function loadSkills() {
    if (!goal) return;
    skillsLoading = true;
    skillsError = '';
    roleSkills = [];
    try {
      const qs: any[] = await apiFetch('/assessments/role/' + encodeURIComponent(goal));
      const names = Array.from(new Set((qs ?? []).map((q) => q.skill).filter(Boolean)));
      const next: Record<string, number> = {};
      for (const n of names) next[n] = answers[n] ?? 0;
      roleSkills = names;
      answers = next;
    } catch (e) {
      skillsError = e instanceof ApiError ? e.detail : t('wizard.levelError');
    } finally {
      skillsLoading = false;
    }
  }

  async function loadAnalysis() {
    if (!goal) return;
    analysis = null;
    analysisError = '';
    try {
      analysis = await apiFetch('/wizard/analysis', {
        method: 'POST',
        body: { goal, weekly_hours: weeklyHours, answers: submitAnswers }
      });
    } catch (e) {
      analysisError = e instanceof ApiError ? e.detail : t('wizard.analysisFailed');
    }
  }

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
      step = 3;
    } catch (e) {
      quizStatus = 'error';
      quizError = e instanceof ApiError ? e.detail : t('wizard.quizError');
    }
  }

  async function goNext() {
    const next = step + 1;
    if (step === 1 && quizMode !== 'quiz') await loadSkills();
    if (next === 4) await loadAnalysis();
    if (next < totalSteps) step = next;
  }

  async function generate() {
    if (!goal) { toastError(t('wizard.goalSubtitle')); return; }
    generating = true;
    // Phase 1: read-only analysis (non-blocking — never hard-fails generation).
    try {
      analysis = await apiFetch('/wizard/analysis', {
        method: 'POST',
        body: { goal, weekly_hours: weeklyHours, answers: submitAnswers }
      });
    } catch (e) {
      analysisError = e instanceof ApiError ? e.detail : t('wizard.analysisFailed');
    }
    // Phase 2: create the (personalized) path with the real answers.
    try {
      const path = await apiFetch('/generate-path/', {
        method: 'POST',
        body: {
          goal,
          weekly_hours: weeklyHours,
          preferences: { is_free: isFree, format, language },
          answers: submitAnswers
        }
      });
      success(t('wizard.successMessage'));
      goto('/learn/' + path.id);
      return;
    } catch (e) {
      toastError(e instanceof ApiError ? e.detail : t('wizard.errorMessage'));
    } finally {
      generating = false;
    }
  }
</script>

<h1>{t('wizard.title')}</h1>
<p class="muted">{t('wizard.stepOf', { current: step + 1, total: totalSteps })}</p>

<div class="stepper">
  {#each steps as s, i}
    <div class="st" class:active={i === step} class:done={i < step}>
      <span class="dot">{#if i < step}<Icon name="check" size={15} />{:else}{i + 1}{/if}</span><span>{s}</span>
    </div>
  {/each}
</div>

<div class="body">
  {#if step === 0}
    <Panel>
      <p class="sub">{t('wizard.step1Subtitle')}</p>
      {#if optionsLoading}
        <div class="center-spin"><Spinner /></div>
      {:else if optionsError}
        <p class="err-state"><Icon name="alert" size={18} /> {optionsError}</p>
      {:else}
        <Select label={t('wizard.fieldLabel')} hint={t('wizard.fieldHint')}
          bind:value={field} placeholder={t('wizard.fieldAll')}
          options={fields.map((f: string) => ({ value: f, label: f }))} />
      {/if}
    </Panel>

  {:else if step === 1}
    <Panel>
      <p class="sub">{t('wizard.step2Subtitle')}</p>
      <Input label={t('wizard.searchRoles')} bind:value={search} placeholder={t('wizard.searchRoles')} />
      {#if optionsLoading}
        <div class="center-spin"><Spinner /></div>
      {:else if optionsError}
        <p class="err-state"><Icon name="alert" size={18} /> {optionsError}</p>
      {:else}
        <div class="roles">
          {#each roles as r}
            <button class="role" class:sel={goal === r.title} onclick={() => (goal = r.title)}>
              <strong>{r.title}</strong>
              {#if r.description}<small class="muted">{r.description}</small>{/if}
            </button>
          {:else}
            <p class="muted">{t('wizard.noResults')}</p>
          {/each}
        </div>
      {/if}
    </Panel>

  {:else if step === 2}
    <Panel>
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
      {:else}
        <p class="sub">{t('wizard.step3Subtitle')}</p>
        {#if skillsLoading}
          <div class="center-spin"><Spinner /></div>
        {:else if skillsError}
          <p class="err-state"><Icon name="alert" size={18} /> {skillsError}</p>
        {:else if roleSkills.length === 0}
          <p class="muted">{t('wizard.levelFallback')}</p>
          <div class="level-row">
            <span class="level-name">{t('wizard.levelOverallLabel')}</span>
            <input type="range" min="0" max="5" step="1" bind:value={overall} class="range" />
            <span class="level-val">{overall}</span>
          </div>
        {:else}
          <p class="muted">{t('wizard.levelInstruction')}</p>
          {#each roleSkills as sk}
            <div class="level-row">
              <span class="level-name">{sk}</span>
              <input type="range" min="0" max="5" step="1" bind:value={answers[sk]} class="range" />
              <span class="level-val">{answers[sk]}</span>
            </div>
          {/each}
        {/if}
      {/if}
    </Panel>

  {:else if step === 3}
    <Panel>
      <p class="sub">{t('wizard.step4Subtitle')}</p>
      <div class="stack">
        <Input label={t('wizard.weeklyHours')} type="number" min={1} max={80} bind:value={weeklyHours} />
        <Select label={t('wizard.formatLabel')} bind:value={format} options={(options?.preferences?.formats ?? ['any', 'video', 'article', 'course']).map((f: string) => ({ value: f, label: f }))} />
        <Select label={t('wizard.languageLabel')} bind:value={language} options={(options?.preferences?.languages ?? ['en', 'ar']).map((l: string) => ({ value: l, label: l }))} />
        <label class="check"><input type="checkbox" bind:checked={isFree} /> {t('wizard.freeContentLabel')}</label>
      </div>
    </Panel>

  {:else}
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
  {/if}
</div>

<div class="nav">
  <Button variant="ghost" onclick={() => step > 0 && step--} disabled={step === 0 || generating}>{t('wizard.back')}</Button>
  {#if step < totalSteps - 1 && !(step === 2 && quizMode === 'quiz')}
    <Button onclick={goNext} disabled={!stepValid || generating}>{t('wizard.next')}</Button>
  {:else if step >= totalSteps - 1}
    <Button onclick={generate} disabled={generating}>
      {#if generating}<Spinner />{:else}<Icon name="sparkles" size={16} />{/if}
      {generating ? t('wizard.generating') : t('wizard.generateButton')}
    </Button>
  {/if}
</div>

<style>
  .stepper { display: flex; gap: 0.5rem; flex-wrap: wrap; margin: 1rem 0; }
  .st { display: flex; align-items: center; gap: 0.5rem; font-size: 0.9rem; color: var(--muted); }
  .st.active { color: var(--ink); font-weight: 600; }
  .dot { width: 26px; height: 26px; border-radius: 50%; border: 1px solid var(--line-strong); display: inline-flex; align-items: center; justify-content: center; font-size: 0.8rem; }
  .st.active .dot { background: var(--accent); color: #fff; border-color: var(--accent); }
  .st.done .dot { background: var(--accent-deep); color: #fff; border-color: var(--accent-deep); }
  .sub { margin: 0 0 0.8rem; color: var(--ink-soft); }
  .roles { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.6rem; margin-top: 0.8rem; }
  .role { text-align: start; border: 1px solid var(--line); background: var(--paper); border-radius: var(--radius); padding: 0.7rem 0.9rem; cursor: pointer; display: flex; flex-direction: column; gap: 0.2rem; font-family: var(--font-body); color: var(--ink); min-height: 44px; transition: border-color 0.18s ease, background 0.18s ease; }
  .role.sel { border-color: var(--accent); background: var(--accent-soft); }
  .role:hover { border-color: var(--accent); }
  .check { display: flex; align-items: center; gap: 0.5rem; color: var(--ink-soft); min-height: 44px; }
  .check input { width: 18px; height: 18px; accent-color: var(--accent); }
  .check:focus-within { outline: none; box-shadow: 0 0 0 3px var(--focus-glow); border-radius: var(--radius); }
  .stack { display: flex; flex-direction: column; gap: 1rem; }
  .review { display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; }
  .review .muted { display: block; font-size: 0.8rem; }
  .level-row { display: grid; grid-template-columns: 1fr 2fr auto; align-items: center; gap: 0.8rem; padding: 0.4rem 0; }
  .level-name { color: var(--ink); font-weight: 500; }
  .level-val { width: 1.5rem; text-align: center; font-weight: 600; color: var(--accent-deep); }
  .range { accent-color: var(--accent); }
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
  .err-state { display: flex; align-items: center; gap: 0.5rem; color: var(--danger); margin-top: 0.8rem; }
  .nav { display: flex; justify-content: space-between; margin-top: 1.2rem; }
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
