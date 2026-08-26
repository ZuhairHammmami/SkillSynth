<!-- Path-generation wizard. Three steps: target role, preferences, summary. -->
<script lang="ts">
  import { apiFetch, ApiError } from '$lib/api/client';
  import { query } from '$lib/query';
  import { goto } from '$app/navigation';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Field from '$lib/components/ui/Field.svelte';
  import Icon from '$lib/icons/Icon.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import { error as toastError, success } from '$lib/components/ui/toast';
  import { t } from '$lib/i18n';

  let options = $state<any>(null);
  let step = $state(0);
  let goal = $state('');
  let search = $state('');
  let weeklyHours = $state(10);
  let isFree = $state(true);
  let format = $state('any');
  let language = $state('en');
  let generating = $state(false);

  const steps = [t('wizard.goalTitle'), t('wizard.preferencesTitle'), t('wizard.summaryTitle')];

  $effect(() => {
    query(['wizardOptions'], () => apiFetch('/wizard-options')).then((d) => (options = d)).catch(() => {});
  });

  let roles = $derived(
    !options ? [] : (options.job_roles ?? []).filter((r: any) =>
      !search || r.title.toLowerCase().includes(search.toLowerCase())
    )
  );

  async function generate() {
    if (!goal) { toastError(t('wizard.goalSubtitle')); return; }
    generating = true;
    try {
      const path = await apiFetch('/generate-path/', {
        method: 'POST',
        body: {
          goal,
          weekly_hours: weeklyHours,
          preferences: { is_free: isFree, format, language },
          answers: {}
        }
      });
      success(t('wizard.successMessage'));
      goto('/learn/' + path.id);
    } catch (e) {
      toastError(e instanceof ApiError ? e.detail : t('wizard.errorMessage'));
    } finally {
      generating = false;
    }
  }
</script>

<h1>{t('wizard.title')}</h1>
<p class="muted">{t('wizard.goalSubtitle')}</p>

<div class="stepper">
  {#each steps as s, i}
    <div class="st" class:active={i === step} class:done={i < step}>
      <span class="dot">{i < step ? '✓' : i + 1}</span><span>{s}</span>
    </div>
  {/each}
</div>

<div class="body">
  {#if step === 0}
    <Panel>
      <Field label={t('wizard.searchRoles')}>
        <Input bind:value={search} placeholder={t('wizard.searchRoles')} />
      </Field>
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
    </Panel>
  {:else if step === 1}
    <Panel>
      <Field label={t('wizard.weeklyHours')}>
        <Input type="number" min={1} max={80} bind:value={weeklyHours} />
      </Field>
      <Field label={t('wizard.formatLabel')}>
        <Select bind:value={format} options={(options?.preferences?.formats ?? ['any', 'video', 'article', 'course']).map((f: string) => ({ value: f, label: f }))} />
      </Field>
      <Field label={t('wizard.languageLabel')}>
        <Select bind:value={language} options={(options?.preferences?.languages ?? ['en', 'ar']).map((l: string) => ({ value: l, label: l }))} />
      </Field>
      <label class="check"><input type="checkbox" bind:checked={isFree} /> {t('wizard.freeContentLabel')}</label>
    </Panel>
  {:else}
    <Panel>
      <div class="review">
        <div><span class="muted">{t('wizard.summaryGoal')}</span><strong>{goal || '—'}</strong></div>
        <div><span class="muted">{t('wizard.summaryHours')}</span><strong>{weeklyHours}h</strong></div>
        <div><span class="muted">{t('wizard.summaryFormat')}</span><strong>{format}</strong></div>
        <div><span class="muted">{t('wizard.summaryLanguage')}</span><strong>{language}</strong></div>
        <div><span class="muted">{t('wizard.summaryFreeContent')}</span><strong>{isFree ? t('wizard.summaryYes') : t('wizard.summaryNo')}</strong></div>
      </div>
    </Panel>
  {/if}
</div>

<div class="nav">
  <Button variant="ghost" onclick={() => step > 0 && step--} disabled={step === 0}>{t('wizard.back')}</Button>
  {#if step < 2}
    <Button onclick={() => step++}>{t('wizard.next')}</Button>
  {:else}
    <Button onclick={generate} disabled={generating}>{#if generating}<Spinner />{:else}<Icon name="sparkles" size={16} />{/if} {t('wizard.generateButton')}</Button>
  {/if}
</div>

<style>
  .stepper { display: flex; gap: 0.5rem; flex-wrap: wrap; margin: 1rem 0; }
  .st { display: flex; align-items: center; gap: 0.5rem; font-size: 0.9rem; color: var(--muted); }
  .st.active { color: var(--ink); font-weight: 600; }
  .dot { width: 26px; height: 26px; border-radius: 50%; border: 1px solid var(--line-strong); display: inline-flex; align-items: center; justify-content: center; font-size: 0.8rem; }
  .st.active .dot { background: var(--ochre); color: #fff; border-color: var(--ochre); }
  .st.done .dot { background: var(--sage); color: #fff; border-color: var(--sage); }
  .roles { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.6rem; margin-top: 0.8rem; }
  .role { text-align: start; border: 1px solid var(--line); background: var(--paper); border-radius: var(--radius); padding: 0.7rem 0.9rem; cursor: pointer; display: flex; flex-direction: column; gap: 0.2rem; font-family: var(--font-body); color: var(--ink); }
  .role.sel { border-color: var(--ochre); background: var(--paper-2); }
  .role:hover { border-color: var(--ochre); }
  .check { display: flex; align-items: center; gap: 0.5rem; color: var(--ink-soft); }
  .review { display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; }
  .review .muted { display: block; font-size: 0.8rem; }
  .nav { display: flex; justify-content: space-between; margin-top: 1.2rem; }
</style>
