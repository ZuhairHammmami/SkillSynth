<!-- Admin skills CRUD: list, create, edit, restricted delete with force. -->
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
  import { success, error as toastError } from '$lib/components/ui/toast';
  import Icon from '$lib/icons/Icon.svelte';
  import { t } from '$lib/i18n';
  import { name, maxLength, range, nonNegative, positiveInt, hexColor } from '$lib/validation';

  let rows = $state<any[]>([]);
  let cats = $state<any[]>([]);
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
  let touched = $state<Record<string, boolean>>({});

  // Live client-side dialog validity (T16); server 422 fieldErrors stay
  // authority. difficulty_level/estimated_hours arrive as strings from the
  // number inputs (numbers on edit) — coerce with String() before validating.
  const nameErr = $derived(name(String(form.name ?? '')));
  const descErr = $derived(maxLength(String(form.description ?? ''), 2000));
  const diffErr = $derived(range(String(form.difficulty_level ?? ''), 0, 5));
  const hoursErr = $derived(nonNegative(String(form.estimated_hours ?? '')));
  const colorErr = $derived(hexColor(String(form.color ?? '')));
  const catErr = $derived(form.category_id != null && form.category_id !== '' ? positiveInt(form.category_id) : null);
  const nameKey = $derived(touched.name || (form.name ?? '') ? nameErr : null);
  const descKey = $derived((form.description ?? '') ? descErr : null);
  const diffKey = $derived(touched.difficulty_level || (form.difficulty_level ?? '') !== '' ? diffErr : null);
  const hoursKey = $derived(touched.estimated_hours || (form.estimated_hours ?? '') !== '' ? hoursErr : null);
  const colorKey = $derived((form.color ?? '') ? colorErr : null);
  const catKey = $derived(form.category_id != null && form.category_id !== '' ? catErr : null);
  const dialogValid = $derived(nameErr === null && descErr === null && diffErr === null && hoursErr === null && colorErr === null && catErr === null);

  async function load() {
    loading = true;
    err = null;
    try {
      [rows, cats] = await Promise.all([
        query(['SKILLS'], () => apiFetch('/admin/skills')),
        query(['CATS_PICK'], () => apiFetch('/admin/categories'))
      ]);
    } catch (e) { err = e instanceof ApiError ? e.detail : t('admin.common.failedLoad', { entity: t('admin.nav.skills') }); }
    finally { loading = false; }
  }
  $effect(() => { load(); });

  function catOptions() {
    return cats.map((c) => ({ value: c.id, label: c.name }));
  }

  function openCreate() { editing = null; formErrors = {}; touched = {}; form = {}; showForm = true; }
  function openEdit(r: any) { editing = r; formErrors = {}; touched = {}; form = { ...r }; showForm = true; }

  async function save() {
    formErrors = {};
    saving = true;
    try {
      if (editing) await apiFetch('/admin/skills/' + editing.id, { method: 'PUT', body: form });
      else await apiFetch('/admin/skills', { method: 'POST', body: form });
      success(t('admin.common.saved')); showForm = false;
      invalidate(['SKILLS']); invalidate(['CATS_PICK']); await load();
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
      await apiFetch('/admin/skills/' + delTarget.id + (force ? '?force=true' : ''), { method: 'DELETE' });
      success(t('admin.common.deleted')); showDelete = false;
      invalidate(['SKILLS']); invalidate(['CATS_PICK']); await load();
    } catch (e) {
      if (e instanceof ApiError && e.status === 409 && e.dependents) dependents = e.dependents;
      else { toastError(e instanceof ApiError ? e.detail : t('admin.common.deleteFailed')); showDelete = false; }
    } finally { deleting = false; }
  }
</script>

<h1>{t('admin.skills.title')}</h1>
<Panel title={t('admin.skills.panel')}>
  <div class="toolbar">
    <Button variant="primary" onclick={openCreate}><Icon name="plus" size={16} /> {t('admin.skills.add')}</Button>
  </div>

  {#if loading}
    <p class="muted">{t('common.loading')}</p>
  {:else if err}
    <div class="err-box" role="alert">
      <p>{err}</p>
      <Button variant="ghost" onclick={load}><Icon name="refresh" size={15} /> {t('common.retry')}</Button>
    </div>
  {:else if rows.length === 0}
    <p class="muted">{t('admin.skills.empty')}</p>
  {:else}
    <div class="table-scroll">
      <table class="grid-table">
        <thead>
          <tr><th>{t('admin.common.id')}</th><th>{t('admin.common.name')}</th><th>{t('admin.common.difficulty')}</th><th>{t('admin.common.hours')}</th><th>{t('admin.common.category')}</th><th></th></tr>
        </thead>
        <tbody>
          {#each rows as r (r.id)}
            <tr>
              <td>{r.id}</td>
              <td>{r.name}</td>
              <td>{r.difficulty_level ?? '—'}</td>
              <td>{r.estimated_hours ?? '—'}</td>
              <td>{r.category_id ?? '—'}</td>
              <td class="actions">
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

<Dialog open={showForm} onclose={() => (showForm = false)} title={editing ? t('admin.skills.edit') : t('admin.skills.add')}>
  <Field label={t('admin.common.name')} error={nameKey ? t(nameKey, { field: t('admin.common.name'), max: 100 }) : formErrors.name}>
    <Input bind:value={form.name} placeholder="JavaScript Basics" onblur={() => (touched.name = true)} />
  </Field>
  <Field label={t('admin.common.description')} error={descKey ? t(descKey, { field: t('admin.common.description'), max: 2000 }) : formErrors.description}>
    <Textarea bind:value={form.description} placeholder="What this skill covers" />
  </Field>
  <div class="row">
    <Field label={t('admin.skills.difficultyLabel')} error={diffKey ? t(diffKey, { field: t('admin.skills.difficultyLabel'), min: 0, max: 5 }) : formErrors.difficulty_level}>
      <Input bind:value={form.difficulty_level} type="number" min="0" max="5" onblur={() => (touched.difficulty_level = true)} />
    </Field>
    <Field label={t('admin.skills.estHours')} error={hoursKey ? t(hoursKey, { field: t('admin.skills.estHours') }) : formErrors.estimated_hours}>
      <Input bind:value={form.estimated_hours} type="number" min="0" onblur={() => (touched.estimated_hours = true)} />
    </Field>
  </div>
  <div class="row">
    <Field label={t('admin.skills.icon')} error={formErrors.icon}>
      <Input bind:value={form.icon} placeholder="emoji or name" />
    </Field>
    <Field label={t('admin.skills.color')} error={colorKey ? t(colorKey, { field: t('admin.skills.color') }) : formErrors.color}>
      <Input bind:value={form.color} placeholder="#5b8def" />
    </Field>
  </div>
  <Field label={t('admin.skills.category')} error={catKey ? t(catKey, { field: t('admin.skills.category') }) : formErrors.category_id}>
    <Select bind:value={form.category_id} options={catOptions()} placeholder="None" />
  </Field>
  {#if Object.keys(formErrors).length}
    <p class="form-err" role="alert">{t('admin.common.checkFields')}</p>
  {/if}
  {#snippet footer()}
    <Button variant="ghost" onclick={() => (showForm = false)} disabled={saving}>{t('common.cancel')}</Button>
    <Button variant="primary" onclick={save} loading={saving} disabled={saving || !dialogValid}>{t('common.save')}</Button>
  {/snippet}
</Dialog>

<Dialog open={showDelete} onclose={() => (showDelete = false)} title={t('admin.skills.delete')}>
  <p>{t('admin.common.deleteConfirm', { name: delTarget?.name })}</p>
  {#if dependents}
    <p class="warn">{t('admin.common.confirmForce', { entity: t('admin.nav.skills') })}</p>
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

<style>
  .toolbar { display: flex; justify-content: flex-end; margin-bottom: 1rem; }
  .table-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  .row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; }
  .grid-table { width: 100%; border-collapse: collapse; font-size: 0.92rem; }
  .grid-table th, .grid-table td { text-align: start; padding: 0.6rem 0.5rem; border-bottom: 1px solid var(--line); }
  .grid-table th { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); }
  .actions { display: flex; gap: 0.4rem; justify-content: flex-end; }
  .muted { color: var(--muted); }
  .warn { color: var(--danger); font-size: 0.9rem; }
  .deps { margin: 0.4rem 0 0; padding-inline-start: 1.1rem; font-size: 0.88rem; color: var(--ink-soft); }
  .form-err { color: var(--danger); font-size: 0.85rem; margin: 0.2rem 0 0; }
  .err-box { background: var(--danger-soft); border: 1px solid var(--danger); color: var(--danger); padding: 1rem; border-radius: var(--radius); display: flex; flex-direction: column; gap: 0.6rem; }
</style>
