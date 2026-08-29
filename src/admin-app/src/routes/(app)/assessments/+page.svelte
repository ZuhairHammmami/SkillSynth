<!-- Admin assessments CRUD: list, create, edit, restricted delete with
     force, and per-assessment question management (add/edit/delete/reorder).
     Reads/writes /admin/assessments*; mirrors the skills CRUD pattern. -->
<script lang="ts">
  import { apiFetch, ApiError, fieldErrorsFrom } from '$lib/api/client';
  import { query, invalidate } from '$lib/query';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Field from '$lib/components/ui/Field.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Dialog from '$lib/components/ui/Dialog.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import AssessmentQuestionsDialog from '$lib/components/assessment-questions-dialog.svelte';
  import { success, error as toastError } from '$lib/components/ui/toast';
  import Icon from '$lib/icons/Icon.svelte';
  import { t } from '$lib/i18n';
  import { name, maxLength, range, positiveInt } from '$lib/validation';

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
  let touched = $state<Record<string, boolean>>({});

  // Live client-side dialog validity (T16); server 422 fieldErrors stay
  // authority. The skill FK is optional so positiveInt only runs when set;
  // passing_score arrives as a string from the number input — coerce first.
  const titleErr = $derived(name(String(form.title ?? '')));
  const descErr = $derived(maxLength(String(form.description ?? ''), 2000));
  const passErr = $derived(range(String(form.passing_score ?? ''), 0, 100));
  const skillErr = $derived(form.skill_id != null && form.skill_id !== '' ? positiveInt(form.skill_id) : null);
  const titleKey = $derived(touched.title || (form.title ?? '') ? titleErr : null);
  const descKey = $derived((form.description ?? '') ? descErr : null);
  const passKey = $derived(touched.passing_score || (form.passing_score ?? '') !== '' ? passErr : null);
  const skillKey = $derived(form.skill_id != null && form.skill_id !== '' ? skillErr : null);
  const dialogValid = $derived(titleErr === null && descErr === null && passErr === null && skillErr === null);

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

  function openCreate() { editing = null; formErrors = {}; touched = {}; form = { title: '', passing_score: 60, description: '' }; showForm = true; }
  function openEdit(r: any) { editing = r; formErrors = {}; touched = {}; form = { skill_id: r.skill_id, title: r.title, description: r.description ?? '', passing_score: r.passing_score ?? 60 }; showForm = true; }

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

  function openQuestions(r: any) {
    focusAssessment = r; showQuestions = true;
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
  <Field label={t('admin.assessments.titleField')} error={titleKey ? t(titleKey, { field: t('admin.assessments.titleField'), max: 100 }) : formErrors.title}>
    <Input bind:value={form.title} placeholder="JavaScript Basics" onblur={() => (touched.title = true)} />
  </Field>
  <Field label={t('admin.assessments.skillLabel')} error={skillKey ? t(skillKey, { field: t('admin.assessments.skillLabel') }) : formErrors.skill_id}>
    <Select bind:value={form.skill_id} options={skillOptions()} placeholder="None" />
  </Field>
  <Field label={t('admin.assessments.typeField')} error={descKey ? t(descKey, { field: t('admin.assessments.typeField'), max: 2000 }) : formErrors.description}>
    <Input bind:value={form.description} placeholder="quiz" />
  </Field>
  <Field label={t('admin.assessments.passingScore')} error={passKey ? t(passKey, { field: t('admin.assessments.passingScore'), min: 0, max: 100 }) : formErrors.pass_score}>
    <Input bind:value={form.passing_score} type="number" min="0" max="100" onblur={() => (touched.passing_score = true)} />
  </Field>
  {#if Object.keys(formErrors).length}
    <p class="form-err" role="alert">{t('admin.common.checkFields')}</p>
  {/if}
  {#snippet footer()}
    <Button variant="ghost" onclick={() => (showForm = false)} disabled={saving}>{t('common.cancel')}</Button>
    <Button variant="primary" onclick={save} loading={saving} disabled={saving || !dialogValid}>{t('common.save')}</Button>
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

{#if showQuestions}
  <AssessmentQuestionsDialog
    bind:open={showQuestions}
    assessment={focusAssessment}
    onchange={() => { invalidate(['ASMT']); load(); }}
  />
{/if}

<style>
  .toolbar { display: flex; justify-content: flex-end; margin-bottom: 1rem; }
  .muted { color: var(--clay); }
  .warn { color: var(--danger); font-size: 0.9rem; }
  .deps { margin: 0.4rem 0 0; padding-inline-start: 1.1rem; font-size: 0.88rem; color: var(--ink-soft); }
  .err-box { background: var(--danger-soft); border: 1px solid var(--danger); color: var(--danger); padding: 1rem; border-radius: var(--radius); display: flex; flex-direction: column; gap: 0.6rem; }
</style>
