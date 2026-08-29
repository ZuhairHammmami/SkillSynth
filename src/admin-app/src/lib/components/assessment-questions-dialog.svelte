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

  function openQCreate() { qEditing = null; qFormErrors = {}; qForm = { prompt: '', options: '', correct_index: 0 }; qDialogOpen = true; }
  function openQEdit(q: any) { qEditing = q; qFormErrors = {}; qForm = { prompt: q.prompt, options: (q.options ?? []).join('\n'), correct_index: q.correct_index ?? 0 }; qDialogOpen = true; }

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
  <Field label={t('admin.assessments.prompt')} error={qFormErrors.prompt}>
    <Textarea bind:value={qForm.prompt} rows="3" placeholder="What does X do?" />
  </Field>
  <Field label={t('admin.assessments.options')} error={qFormErrors.options}>
    <Textarea bind:value={qForm.options} rows="4" placeholder="Option A&#10;Option B&#10;Option C" />
  </Field>
  <Field label={t('admin.assessments.correctIndex')} error={qFormErrors.correct_index}>
    <Input bind:value={qForm.correct_index} type="number" min="0" />
  </Field>
  {#if Object.keys(qFormErrors).length}
    <p class="form-err" role="alert">{t('admin.common.checkFields')}</p>
  {/if}
  {#snippet footer()}
    <Button variant="ghost" onclick={() => (qDialogOpen = false)} disabled={qSaving}>{t('common.cancel')}</Button>
    <Button variant="primary" onclick={saveQuestion} loading={qSaving}>{t('common.save')}</Button>
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
