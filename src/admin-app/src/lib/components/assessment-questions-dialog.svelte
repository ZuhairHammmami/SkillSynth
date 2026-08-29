<!-- Admin per-assessment question management dialog: list, add, edit,
     delete and reorder questions for a focused assessment. Self-contained
     data fetch; the parent drives open/close and re-validates its listing
     via the onchange callback after any mutation. -->
<script lang="ts">
  import { apiFetch, ApiError, fieldErrorsFrom } from '$lib/api/client';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Textarea from '$lib/components/ui/Textarea.svelte';
  import Field from '$lib/components/ui/Field.svelte';
  import Dialog from '$lib/components/ui/Dialog.svelte';
  import Icon from '$lib/icons/Icon.svelte';
  import { success, error as toastError } from '$lib/components/ui/toast';
  import { t } from '$lib/i18n';
  import { maxLength, options as validateOptions } from '$lib/validation';

  let { open = $bindable(false), assessment = undefined, onchange = () => {} }: {
    open?: boolean;
    assessment?: any;
    onchange?: () => void;
  } = $props();

  let questions = $state<any[]>([]);
  let qLoading = $state(false);

  let qDialogOpen = $state(false);
  let qEditing = $state<any>(null);
  let qForm = $state<any>({});
  let qFormErrors = $state<Record<string, string>>({});
  let qSaving = $state(false);
  let qTouched = $state<Record<string, boolean>>({});

  // Live client-side question validity (T16); server 422/400 stay authority.
  // The correct-option index re-derives its [0, options.length) bounds live as
  // the options textarea changes; the whole question gates the Save button.
  const qOpts = $derived(qPayload().options);
  const qOptsLen = $derived(qOpts.length);
  const qOptMax = $derived(Math.max(0, qOptsLen - 1));
  const promptErr = $derived((qForm.prompt ?? '').trim() ? maxLength(String(qForm.prompt ?? ''), 2000) : 'admin.validation.required');
  const tooLongOption = $derived(qOpts.some((o: string) => o.length > 500) ? 'admin.validation.maxLen' : null);
  const optionsErr = $derived(tooLongOption ?? validateOptions(qOpts));
  const correctErr = $derived(
    qForm.correct_index === '' || qForm.correct_index == null
      ? 'admin.validation.required'
      : Number.isInteger(Number(qForm.correct_index)) && Number(qForm.correct_index) >= 0 && Number(qForm.correct_index) < qOptsLen
        ? null
        : 'admin.validation.minMax'
  );
  const promptKey = $derived(qTouched.prompt || (qForm.prompt ?? '') ? promptErr : null);
  const optionsKey = $derived(qTouched.options || qOptsLen ? optionsErr : null);
  const correctKey = $derived(qTouched.correct_index || qOptsLen ? correctErr : null);
  const qValid = $derived(promptErr === null && optionsErr === null && correctErr === null);

  $effect(() => {
    if (open && assessment) refreshQuestions();
  });

  async function refreshQuestions() {
    if (!assessment) return;
    qLoading = true;
    try {
      const d = await apiFetch('/admin/assessments/' + assessment.id);
      questions = d.questions ?? [];
    } catch (e) { toastError(e instanceof ApiError ? e.detail : t('admin.common.failedLoad', { entity: t('admin.assessments.questions') })); }
    finally { qLoading = false; }
  }

  function openQCreate() { qEditing = null; qFormErrors = {}; qTouched = {}; qForm = { prompt: '', options: '', correct_index: 0 }; qDialogOpen = true; }
  function openQEdit(q: any) { qEditing = q; qFormErrors = {}; qTouched = {}; qForm = { prompt: q.prompt, options: (q.options ?? []).join('\n'), correct_index: q.correct_index ?? 0 }; qDialogOpen = true; }

  function qPayload() {
    const opts = (qForm.options ?? '').split('\n').map((s: string) => s.trim()).filter(Boolean);
    return { ...qForm, options: opts };
  }

  async function saveQuestion() {
    qFormErrors = {};
    qSaving = true;
    const body = qPayload();
    try {
      if (qEditing) await apiFetch(`/admin/assessments/${assessment.id}/questions/${qEditing.id}`, { method: 'PUT', body });
      else await apiFetch(`/admin/assessments/${assessment.id}/questions`, { method: 'POST', body });
      success(t('admin.common.saved')); qDialogOpen = false;
      onchange(); await refreshQuestions();
    } catch (e) {
      if (e instanceof ApiError) {
        const fe = fieldErrorsFrom(e.detail);
        if (Object.keys(fe).length) { qFormErrors = fe; return; }
        toastError(typeof e.detail === 'string' ? e.detail : t('admin.common.saveFailed'));
      } else { toastError(t('admin.common.saveFailed')); }
    } finally { qSaving = false; }
  }

  async function deleteQuestion(q: any) {
    if (!confirm(t('admin.assessments.deleteQuestionConfirm', { id: q.id }))) return;
    try {
      await apiFetch(`/admin/assessments/${assessment.id}/questions/${q.id}`, { method: 'DELETE' });
      success(t('admin.common.deleted'));
      onchange(); await refreshQuestions();
    } catch (e) { toastError(e instanceof ApiError ? e.detail : t('admin.common.deleteFailed')); }
  }

  async function moveQuestion(q: any, dir: number) {
    const target = questions.findIndex((x) => x.id === q.id) + dir;
    if (target < 0 || target >= questions.length) return;
    try {
      await apiFetch(`/admin/assessments/${assessment.id}/questions/${q.id}`, { method: 'PUT', body: { position: target + 1 } });
      onchange(); await refreshQuestions();
    } catch (e) { toastError(e instanceof ApiError ? e.detail : t('admin.common.saveFailed')); }
  }
</script>

<Dialog open={open} onclose={() => (open = false)} title={t('admin.assessments.questionsTitle', { id: assessment?.id })}>
  <div class="toolbar">
    <Button variant="primary" size="sm" onclick={openQCreate}><Icon name="plus" size={15} /> {t('admin.assessments.addQuestion')}</Button>
  </div>
  {#if qLoading}
    <p class="muted">{t('common.loading')}</p>
  {:else if questions.length === 0}
    <p class="muted">{t('admin.assessments.noQuestions')}</p>
  {:else}
    <p class="hint">{t('admin.assessments.reorderHint')}</p>
    <div class="table-scroll">
      <table class="grid-table">
        <thead>
          <tr><th>{t('admin.assessments.positionLabel')}</th><th>{t('admin.assessments.prompt')}</th><th>{t('admin.assessments.correctIndex')}</th><th></th></tr>
        </thead>
        <tbody>
          {#each questions as q, qi (q.id)}
            <tr>
              <td>{q.position}</td>
              <td class="prompt-cell"><span class="idx">{qi + 1}.</span> {q.prompt}</td>
              <td>{q.correct_index}</td>
              <td class="actions">
                <Button variant="ghost" size="sm" onclick={() => moveQuestion(q, -1)} disabled={qi === 0}><Icon name="chevronUp" size={15} /></Button>
                <Button variant="ghost" size="sm" onclick={() => moveQuestion(q, 1)} disabled={qi === questions.length - 1}><Icon name="chevronDown" size={15} /></Button>
                <Button variant="ghost" size="sm" onclick={() => openQEdit(q)}><Icon name="edit" size={15} /></Button>
                <Button variant="destructive" size="sm" onclick={() => deleteQuestion(q)}><Icon name="trash" size={15} /></Button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
  {#snippet footer()}
    <Button variant="ghost" onclick={() => (open = false)}>{t('common.close')}</Button>
  {/snippet}
</Dialog>

<Dialog open={qDialogOpen} onclose={() => (qDialogOpen = false)} title={qEditing ? t('admin.assessments.editQuestion') : t('admin.assessments.addQuestion')}>
  <Field label={t('admin.assessments.prompt')} error={promptKey ? t(promptKey, { field: t('admin.assessments.prompt'), max: 2000 }) : qFormErrors.prompt}>
    <Textarea bind:value={qForm.prompt} rows="3" placeholder="What does X do?" onblur={() => (qTouched.prompt = true)} />
  </Field>
  <Field label={t('admin.assessments.options')} error={optionsKey ? t(optionsKey, { field: t('admin.assessments.options'), min: 2, max: 500 }) : qFormErrors.options}>
    <Textarea bind:value={qForm.options} rows="4" placeholder="Option A&#10;Option B&#10;Option C" onblur={() => (qTouched.options = true)} />
  </Field>
  <Field label={t('admin.assessments.correctIndex')} error={correctKey ? t(correctKey, { field: t('admin.assessments.correctIndex'), min: 0, max: qOptMax }) : qFormErrors.correct_index}>
    <Input bind:value={qForm.correct_index} type="number" min="0" onblur={() => (qTouched.correct_index = true)} />
  </Field>
  {#if Object.keys(qFormErrors).length}
    <p class="form-err" role="alert">{t('admin.common.checkFields')}</p>
  {/if}
  {#snippet footer()}
    <Button variant="ghost" onclick={() => (qDialogOpen = false)} disabled={qSaving}>{t('common.cancel')}</Button>
    <Button variant="primary" onclick={saveQuestion} loading={qSaving} disabled={qSaving || !qValid}>{t('common.save')}</Button>
  {/snippet}
</Dialog>

<style>
  .toolbar { display: flex; justify-content: flex-end; margin-bottom: 1rem; }
  .table-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  .grid-table { width: 100%; border-collapse: collapse; font-size: 0.92rem; }
  .grid-table th, .grid-table td { text-align: start; padding: 0.6rem 0.5rem; border-bottom: 1px solid var(--line); }
  .grid-table th { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); }
  .actions { display: flex; gap: 0.4rem; justify-content: flex-end; align-items: center; }
  .muted { color: var(--muted); }
  .hint { color: var(--muted); font-size: 0.8rem; margin: 0 0 0.5rem; }
  .form-err { color: var(--danger); font-size: 0.85rem; margin: 0.2rem 0 0; }
  .prompt-cell { max-width: 22rem; }
  .idx { color: var(--muted); }
</style>
