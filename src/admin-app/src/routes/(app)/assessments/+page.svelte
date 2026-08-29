<!-- Admin assessments CRUD: list, create, edit, restricted delete with
     force, and per-assessment question management (add/edit/delete/reorder).
     Reads/writes /admin/assessments*; mirrors the skills CRUD pattern. -->
<script lang="ts">
  import { apiFetch, ApiError, fieldErrorsFrom } from '$lib/api/client';
  import { query, invalidate } from '$lib/query';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Textarea from '$lib/components/ui/Textarea.svelte';
  import Field from '$lib/components/ui/Field.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Dialog from '$lib/components/ui/Dialog.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import { success, error as toastError } from '$lib/components/ui/toast';
  import Icon from '$lib/icons/Icon.svelte';
  import { t } from '$lib/i18n';

  let rows = $state<any[]>([]);
  let skills = $state<any[]>([]);
  let loading = $state(true);
  let err = $state<string | null>(null);

  let showForm = $state(false);
  let editing = $state<any>(null);
  let form = $state<any>({});
  let formErrors = $state<Record<string, string>>({});
  let saving = $state(false);

  let showDelete = $state(false);
  let delTarget = $state<any>(null);
  let deleting = $state(false);
  let dependents = $state<Record<string, number> | null>(null);

  let showQuestions = $state(false);
  let focusAssessment = $state<any>(null);
  let questions = $state<any[]>([]);
  let qLoading = $state(false);

  let qDialogOpen = $state(false);
  let qEditing = $state<any>(null);
  let qForm = $state<any>({});
  let qFormErrors = $state<Record<string, string>>({});
  let qSaving = $state(false);

  async function load() {
    loading = true;
    err = null;
    try {
      [rows, skills] = await Promise.all([
        query(['ASMT'], () => apiFetch('/admin/assessments')),
        query(['SKILLS_PICK'], () => apiFetch('/admin/skills'))
      ]);
    } catch (e) {
      err = e instanceof ApiError ? e.detail : t('admin.common.failedLoad', { entity: t('admin.nav.assessments') });
    } finally {
      loading = false;
    }
  }
  $effect(() => { load(); });

  function skillOptions(): { value: number; label: string }[] {
    return skills.map((s) => ({ value: s.id, label: s.name }));
  }

  function openCreate() { editing = null; formErrors = {}; form = { title: '', passing_score: 60, description: '' }; showForm = true; }
  function openEdit(r: any) { editing = r; formErrors = {}; form = { skill_id: r.skill_id, title: r.title, description: r.description ?? '', passing_score: r.passing_score ?? 60 }; showForm = true; }

  async function save() {
    formErrors = {};
    saving = true;
    const body: any = { ...form, pass_score: Number(form.passing_score ?? 60) };
    try {
      if (editing) {
        delete body.questions;
        await apiFetch('/admin/assessments/' + editing.id, { method: 'PUT', body });
      } else {
        await apiFetch('/admin/assessments', { method: 'POST', body });
      }
      success(t('admin.common.saved')); showForm = false;
      invalidate(['ASMT']); await load();
    } catch (e) {
      if (e instanceof ApiError) {
        const fe = fieldErrorsFrom(e.detail);
        if (Object.keys(fe).length) { formErrors = fe; return; }
        toastError(typeof e.detail === 'string' ? e.detail : t('admin.common.saveFailed'));
      } else { toastError(t('admin.common.saveFailed')); }
    } finally { saving = false; }
  }

  async function askDelete(r: any) { delTarget = r; dependents = null; showDelete = true; }
  async function doDelete(force: boolean) {
    deleting = true;
    try {
      await apiFetch('/admin/assessments/' + delTarget.id + (force ? '?force=true' : ''), { method: 'DELETE' });
      success(t('admin.common.deleted')); showDelete = false;
      invalidate(['ASMT']); await load();
    } catch (e) {
      if (e instanceof ApiError && e.status === 409 && e.dependents) dependents = e.dependents;
      else { toastError(e instanceof ApiError ? e.detail : t('admin.common.deleteFailed')); showDelete = false; }
    } finally { deleting = false; }
  }

  async function openQuestions(r: any) {
    focusAssessment = r; showQuestions = true;
    await refreshQuestions();
  }
  async function refreshQuestions() {
    if (!focusAssessment) return;
    qLoading = true;
    try {
      const d = await apiFetch('/admin/assessments/' + focusAssessment.id);
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
      if (qEditing) await apiFetch(`/admin/assessments/${focusAssessment.id}/questions/${qEditing.id}`, { method: 'PUT', body });
      else await apiFetch(`/admin/assessments/${focusAssessment.id}/questions`, { method: 'POST', body });
      success(t('admin.common.saved')); qDialogOpen = false;
      invalidate(['ASMT']); await refreshQuestions();
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
      await apiFetch(`/admin/assessments/${focusAssessment.id}/questions/${q.id}`, { method: 'DELETE' });
      success(t('admin.common.deleted'));
      invalidate(['ASMT']); await refreshQuestions();
    } catch (e) { toastError(e instanceof ApiError ? e.detail : t('admin.common.deleteFailed')); }
  }

  async function moveQuestion(q: any, dir: number) {
    const base = focusAssessment.id;
    const target = questions.findIndex((x) => x.id === q.id) + dir;
    if (target < 0 || target >= questions.length) return;
    try {
      await apiFetch(`/admin/assessments/${base}/questions/${q.id}`, { method: 'PUT', body: { position: target + 1 } });
      invalidate(['ASMT']); await refreshQuestions();
    } catch (e) { toastError(e instanceof ApiError ? e.detail : t('admin.common.saveFailed')); }
  }
</script>

<h1>{t('admin.assessments.title')}</h1>
<Panel title={t('admin.assessments.panel')}>
  <div class="toolbar">
    <Button variant="primary" onclick={openCreate}><Icon name="plus" size={16} /> {t('admin.assessments.add')}</Button>
  </div>

  {#if loading}
    <p class="muted">{t('common.loading')}</p>
  {:else if err}
    <div class="err-box" role="alert">
      <p>{err}</p>
      <Button variant="ghost" onclick={load}><Icon name="refresh" size={15} /> {t('common.retry')}</Button>
    </div>
  {:else if rows.length === 0}
    <p class="muted">{t('admin.assessments.empty')}</p>
  {:else}
    <div class="table-scroll">
      <table class="grid-table">
        <thead>
          <tr>
            <th>{t('admin.common.id')}</th><th>{t('admin.common.title')}</th>
            <th>{t('admin.common.skill')}</th><th>{t('admin.common.type')}</th>
            <th>{t('admin.common.passing')}</th><th>{t('admin.assessments.questions')}</th><th></th>
          </tr>
        </thead>
        <tbody>
          {#each rows as r (r.id)}
            <tr>
              <td>{r.id}</td>
              <td>{r.title ?? '—'}</td>
              <td>{r.skill_name ?? r.skill_id ?? '—'}</td>
              <td><Badge tone="neutral">{r.assessment_type ?? '—'}</Badge></td>
              <td>{r.passing_score ?? '—'}</td>
              <td>{r.question_count ?? 0}</td>
              <td class="actions">
                <Button variant="ghost" size="sm" onclick={() => openQuestions(r)}><Icon name="quiz" size={15} /> {t('admin.assessments.questions')}</Button>
                <Button variant="ghost" size="sm" onclick={() => openEdit(r)}><Icon name="edit" size={15} /> {t('common.edit')}</Button>
                <Button variant="destructive" size="sm" onclick={() => askDelete(r)}><Icon name="trash" size={15} /> {t('common.delete')}</Button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</Panel>

<Dialog open={showForm} onclose={() => (showForm = false)} title={editing ? t('admin.assessments.edit') : t('admin.assessments.add')}>
  <Field label={t('admin.assessments.titleField')} error={formErrors.title}>
    <Input bind:value={form.title} placeholder="JavaScript Basics" />
  </Field>
  <Field label={t('admin.assessments.skillLabel')} error={formErrors.skill_id}>
    <Select bind:value={form.skill_id} options={skillOptions()} placeholder="None" />
  </Field>
  <Field label={t('admin.assessments.typeField')} error={formErrors.description}>
    <Input bind:value={form.description} placeholder="quiz" />
  </Field>
  <Field label={t('admin.assessments.passingScore')} error={formErrors.pass_score}>
    <Input bind:value={form.passing_score} type="number" min="0" max="100" />
  </Field>
  {#if Object.keys(formErrors).length}
    <p class="form-err" role="alert">{t('admin.common.checkFields')}</p>
  {/if}
  {#snippet footer()}
    <Button variant="ghost" onclick={() => (showForm = false)} disabled={saving}>{t('common.cancel')}</Button>
    <Button variant="primary" onclick={save} loading={saving}>{t('common.save')}</Button>
  {/snippet}
</Dialog>

<Dialog open={showDelete} onclose={() => (showDelete = false)} title={t('admin.assessments.delete')}>
  <p>{t('admin.assessments.deleteConfirm', { id: delTarget?.id })}</p>
  {#if dependents}
    <p class="warn">{t('admin.common.confirmForce', { entity: t('admin.nav.assessments') })}</p>
    <ul class="deps">
      {#each Object.entries(dependents) as [k, v]}
        <li>{k}: {v}</li>
      {/each}
    </ul>
  {/if}
  {#snippet footer()}
    <Button variant="ghost" onclick={() => (showDelete = false)} disabled={deleting}>{t('common.cancel')}</Button>
    {#if dependents}
      <Button variant="destructive" onclick={() => doDelete(true)} loading={deleting}>{t('common.forceDelete')}</Button>
    {:else}
      <Button variant="destructive" onclick={() => doDelete(false)} loading={deleting}>{t('common.delete')}</Button>
    {/if}
  {/snippet}
</Dialog>

<Dialog open={showQuestions} onclose={() => (showQuestions = false)} title={t('admin.assessments.questionsTitle', { id: focusAssessment?.id })}>
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
    <Button variant="ghost" onclick={() => (showQuestions = false)}>{t('common.close')}</Button>
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
  .warn { color: var(--danger); font-size: 0.9rem; }
  .deps { margin: 0.4rem 0 0; padding-inline-start: 1.1rem; font-size: 0.88rem; color: var(--ink-soft); }
  .form-err { color: var(--danger); font-size: 0.85rem; margin: 0.2rem 0 0; }
  .prompt-cell { max-width: 22rem; }
  .idx { color: var(--muted); }
  .err-box { background: var(--danger-soft); border: 1px solid var(--danger); color: var(--danger); padding: 1rem; border-radius: var(--radius); display: flex; flex-direction: column; gap: 0.6rem; }
</style>
