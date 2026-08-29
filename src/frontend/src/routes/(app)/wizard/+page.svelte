<script lang="ts">
  import { apiFetch, ApiError } from '$lib/api/client';
  import { query } from '$lib/query';
  import { goto } from '$app/navigation';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Icon from '$lib/icons/Icon.svelte';
  import { error as toastError, success } from '$lib/components/ui/toast';
  import { t } from '$lib/i18n';
  import { weeklyHours as validateWeeklyHours } from '$lib/validation';
  import QuizStep from './QuizStep.svelte';
  import ReviewStep from './ReviewStep.svelte';

  const totalSteps = 5;

  let options = $state<any>(null);
  let step = $state(0);

  let field = $state('');
  let goal = $state('');
  let search = $state('');
  let answers = $state<Record<string, number>>({});
  let roleSkills = $state<string[]>([]);
  let skillsLoading = $state(false);
  let skillsError = $state('');
  let overall = $state(0);
  let weeklyHours = $state(10);
  let isFree = $state(true);
  let format = $state('any');
  let language = $state('en');
  let analysis = $state<any>(null);
  let analysisError = $state('');
  let generateError = $state('');

  let aiEnabled = $state<boolean | null>(null);
  let quizMode = $state<'quiz' | 'self' | null>(null);

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
      .then((d) => { aiEnabled = !!(d && d.ai_enabled); })
      .catch(() => { aiEnabled = false; });
  });

  let fields = $derived(!options ? [] : Object.keys(options.career_fields ?? {}));
  let rolesForField = $derived(
    !options ? [] : (field ? (options.career_fields?.[field] ?? []) : (options.job_roles ?? []))
  );
  let roles = $derived(
    rolesForField.filter((r: any) =>
      !search || r.title.toLowerCase().includes(search.toLowerCase()))
  );
  let submitAnswers = $derived(answers);
  const hoursError = $derived(validateWeeklyHours(String(weeklyHours), 1, 80));
  const hoursValid = $derived(validateWeeklyHours(String(weeklyHours), 1, 80) === null);
  let stepValid = $derived(
    step === 0 ? !!field :
    step === 1 ? !!goal :
    step === 2 ? (quizMode !== null) :
    true
  );

  /**
   * Loads the assessment questions for the chosen role and merges the role's
   * skills into the shared answer map, keeping any self-assessment levels the
   * user already chose for skills that persist across loads.
   */
  async function loadSkills() {
    if (!goal) return;
    skillsLoading = true;
    skillsError = '';
    try {
      const qs: any[] = await apiFetch('/assessments/role/' + encodeURIComponent(goal));
      const names = Array.from(new Set((qs ?? []).map((q) => q.skill).filter(Boolean)));
      const next: Record<string, number> = { ...answers };
      for (const n of names) if (!(n in next)) next[n] = 0;
      roleSkills = names;
      answers = next;
    } catch (e) {
      skillsError = e instanceof ApiError ? e.detail : t('wizard.levelError');
    } finally {
      skillsLoading = false;
    }
  }

  /** Requests a read-only path analysis for the chosen goal, hours and answers and
   * stores the resulting recommendations for the summary step. */
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

  /**
   * Advances the wizard to the next step, loading supporting data (role skills or
   * analysis) exactly when those steps are reached.
   */
  async function goNext() {
    const next = step + 1;
    if (step === 1 && quizMode !== 'quiz') await loadSkills();
    if (next === 4) await loadAnalysis();
    if (next < totalSteps) step = next;
  }

  /** Generates the personalized learning path, navigating on success or surfacing failures inline + toast. */
  async function generate() {
    if (!goal) { toastError(t('wizard.goalSubtitle')); return; }
    generating = true;
    generateError = '';
    const weeklyHoursInt = Math.floor(Number(weeklyHours)) || 0;
    const sendAnswers = (roleSkills.length === 0 && goal)
      ? { ...submitAnswers, [goal]: overall }
      : submitAnswers;
    try {
      const path = await apiFetch('/generate-path/', {
        method: 'POST',
        body: {
          goal,
          weekly_hours: weeklyHoursInt,
          preferences: { is_free: isFree, format, language },
          answers: sendAnswers
        }
      });
      success(t('wizard.successMessage'));
      goto('/learn/' + path.id);
      return;
    } catch (e) {
      const msg = e instanceof ApiError ? e.detail : t('wizard.errorMessage');
      generateError = msg;
      toastError(msg);
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
      <Input label={t('wizard.searchRoles')} bind:value={search} placeholder={t('wizard.searchRoles')} hint={t('wizard.searchHint')} />
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
      {#if quizMode === null || quizMode === 'quiz'}
        <QuizStep bind:quizMode {goal} {aiEnabled} {weeklyHours}
          bind:answers bind:roleSkills bind:analysis
          onComplete={() => (step = 3)} />
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
        <Input label={t('wizard.weeklyHours')} type="number" min={1} max={80} bind:value={weeklyHours} error={hoursError ? t(hoursError) : ''} />
        <Select label={t('wizard.formatLabel')} bind:value={format} options={(options?.preferences?.formats ?? ['any', 'video', 'article', 'course']).map((f: string) => ({ value: f, label: f }))} />
        <Select label={t('wizard.languageLabel')} bind:value={language} options={(options?.preferences?.languages ?? ['en', 'ar']).map((l: string) => ({ value: l, label: l }))} />
        <label class="check"><input type="checkbox" bind:checked={isFree} /> {t('wizard.freeContentLabel')}</label>
      </div>
    </Panel>

  {:else}
    <ReviewStep {field} {goal} {roleSkills} {overall} {weeklyHours}
      {format} {language} {isFree} {analysis} {analysisError} />
  {/if}
</div>

<div class="nav">
  {#if generateError}<p class="err-state"><Icon name="alert" size={18} /> {generateError}</p>{/if}
  <Button variant="ghost" onclick={() => step > 0 && step--} disabled={step === 0 || generating}>{t('wizard.back')}</Button>
  {#if step < totalSteps - 1 && !(step === 2 && quizMode === 'quiz')}
    <Button onclick={goNext} disabled={!stepValid || generating}>{t('wizard.next')}</Button>
  {:else if step >= totalSteps - 1}
    <Button onclick={generate} disabled={generating || !hoursValid}>
      {#if generating}<Spinner />{:else}<Icon name="sparkles" size={16} />{/if}
      {generating ? t('wizard.generating') : t('wizard.generateButton')}
    </Button>
  {/if}
</div>

<style>
  .stepper { display: flex; gap: 0.5rem; flex-wrap: wrap; margin: 1rem 0; }
  .st { display: flex; align-items: center; gap: 0.5rem; font-size: 0.9rem; color: var(--clay); }
  .st.active { color: var(--ink); font-weight: 600; }
  .dot { width: 26px; height: 26px; border-radius: 50%; border: 1px solid var(--line-strong); display: inline-flex; align-items: center; justify-content: center; font-size: 0.8rem; }
  .st.active .dot { background: var(--ochre); color: #fff; border-color: var(--ochre); }
  .st.done .dot { background: var(--ochre-deep); color: #fff; border-color: var(--ochre-deep); }
  .sub { margin: 0 0 0.8rem; color: var(--ink-soft); }
  .roles { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.6rem; margin-top: 0.8rem; }
  .role { text-align: start; border: 1px solid var(--line); background: var(--card); border-radius: var(--radius); padding: 0.7rem 0.9rem; cursor: pointer; display: flex; flex-direction: column; gap: 0.2rem; font-family: var(--font-body); color: var(--ink); min-height: 44px; transition: border-color 0.18s ease, background 0.18s ease; }
  .role.sel { border-color: var(--ochre); background: var(--ochre-soft); }
  .role:hover { border-color: var(--ochre); }
  .check { display: flex; align-items: center; gap: 0.5rem; color: var(--ink-soft); min-height: 44px; }
  .check input { width: 18px; height: 18px; accent-color: var(--ochre); }
  .check:focus-within { outline: none; box-shadow: 0 0 0 3px var(--focus-glow); border-radius: var(--radius); }
  .stack { display: flex; flex-direction: column; gap: 1rem; }
  .level-row { display: grid; grid-template-columns: 1fr 2fr auto; align-items: center; gap: 0.8rem; padding: 0.4rem 0; }
  .level-name { color: var(--ink); font-weight: 500; }
  .level-val { width: 1.5rem; text-align: center; font-weight: 600; color: var(--ochre-deep); }
  .range { accent-color: var(--ochre); }
  .err-state { display: flex; align-items: center; gap: 0.5rem; color: var(--danger); margin-top: 0.8rem; }
  .nav { display: flex; justify-content: space-between; margin-top: 1.2rem; }
  .center-spin { display: flex; justify-content: center; padding: 1.2rem; }
</style>
