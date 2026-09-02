<!-- Admin job-roles CRUD: list, create, edit, restricted delete with force.
     Skills are chosen via a multi-select of existing skills (no free-text ids). -->
<script lang="ts">
  import { apiFetch, ApiError, fieldErrorsFrom } from '$lib/api/client';
  import { query, invalidate } from '$lib/query';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Textarea from '$lib/components/ui/Textarea.svelte';
  import Field from '$lib/components/ui/Field.svelte';
  import Dialog from '$lib/components/ui/Dialog.svelte';
  import { success, error as toastError } from '$lib/components/ui/toast';
  import Icon from '$lib/icons/Icon.svelte';
  import { t } from '$lib/i18n';
  import { name, maxLength } from '$lib/validation';

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
  let skillFilter = $state('');
  let touched = $state<Record<string, boolean>>({});

  // Live client-side dialog validity (T16); server 422 fieldErrors stay authority.
  const titleErr = $derived(name(String(form.title ?? '')));
  const careerErr = $derived(maxLength(String(form.career_field ?? ''), 150));
  const descErr = $derived(maxLength(String(form.description ?? ''), 2000));
  const titleKey = $derived(touched.title || (form.title ?? '') ? titleErr : null);
  const careerKey = $derived((form.career_field ?? '') ? careerErr : null);
  const descKey = $derived((form.description ?? '') ? descErr : null);
  const dialogValid = $derived(titleErr === null && careerErr === null && descErr === null);

  async function load() {
    loading = true;
    err = null;
    try {
      const [r, sk] = await Promise.all([
        query(['ROLES'], () => apiFetch('/admin/job-roles')),
        query(['SKILLS_PICK_ROLES'], () => apiFetch('/admin/skills'))
      ]);
      rows = r.items;
      skills = sk.items;
    } catch (e) { err = e instanceof ApiError ? e.detail : t('admin.common.failedLoad', { entity: t('admin.nav.jobRoles') }); }
    finally { loading = false; }
  }
  $effect(() => { load(); });

  const filteredSkills = $derived(
    (skills || []).filter((s) => s.name.toLowerCase().includes(skillFilter.trim().toLowerCase()))
  );

  function selectedIds(): number[] {
    return Array.isArray(form.skill_ids) ? form.skill_ids : [];
  }
  function toggleSkill(id: number) {
    const cur = selectedIds();
    form.skill_ids = cur.includes(id) ? cur.filter((x) => x !== id) : [...cur, id];
  }

  function openCreate() { editing = null; formErrors = {}; touched = {}; form = { skill_ids: [] }; showForm = true; }
  function openEdit(r: any) {
    editing = r;
    formErrors = {};
    touched = {};
    form = { ...r, skill_ids: Array.isArray(r.skill_ids) ? r.skill_ids.map(Number) : [] };
    showForm = true;
  }

  async function save() {
    formErrors = {};
    saving = true;
    const payload = { ...form, skill_ids: selectedIds() };
    try {
      if (editing) await apiFetch('/admin/job-roles/' + editing.id, { method: 'PUT', body: payload });
      else await apiFetch('/admin/job-roles', { method: 'POST', body: payload });
      success(t('admin.common.saved')); showForm = false;
      invalidate(['ROLES']); invalidate(['SKILLS_PICK_ROLES']); await load();
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
      await apiFetch('/admin/job-roles/' + delTarget.id + (force ? '?force=true' : ''), { method: 'DELETE' });
      success(t('admin.common.deleted')); showDelete = false;
      invalidate(['ROLES']); invalidate(['SKILLS_PICK_ROLES']); await load();
    } catch (e) {
      if (e instanceof ApiError && e.status === 409 && e.dependents) dependents = e.dependents;
      else { toastError(e instanceof ApiError ? e.detail : t('admin.common.deleteFailed')); showDelete = false; }
    } finally { deleting = false; }
  }
</script>

<h1>{t('admin.jobRoles.title')}</h1>
<Panel title={t('admin.jobRoles.panel')}>
  <div class="toolbar">
    <Button variant="primary" onclick={openCreate}><Icon name="plus" size={16} /> {t('admin.jobRoles.add')}</Button>
  </div>

  {#if loading}
    <p class="muted">{t('common.loading')}</p>
  {:else if err}
    <div class="err-box" role="alert">
      <p>{err}</p>
      <Button variant="ghost" onclick={load}><Icon name="refresh" size={15} /> {t('common.retry')}</Button>
    </div>
  {:else if rows.length === 0}
    <p class="muted">{t('admin.jobRoles.empty')}</p>
  {:else}
    <div class="table-scroll">
      <table class="grid-table">
        <thead>
          <tr><th>{t('admin.common.id')}</th><th>{t('admin.common.title')}</th><th>{t('admin.jobRoles.careerField')}</th><th>{t('admin.nav.skills')}</th><th></th></tr>
        </thead>
        <tbody>
          {#each rows as r (r.id)}
            <tr>
              <td>{r.id}</td>
              <td>{r.title}</td>
              <td>{r.career_field ?? '—'}</td>
              <td>{(r.skill_ids ?? []).length}</td>
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

<Dialog open={showForm} onclose={() => (showForm = false)} title={editing ? t('admin.jobRoles.edit') : t('admin.jobRoles.add')}>
  <Field label={t('admin.common.title')} error={titleKey ? t(titleKey, { field: t('admin.common.title'), max: 100 }) : formErrors.title}>
    <Input bind:value={form.title} placeholder="Frontend Engineer" onblur={() => (touched.title = true)} />
  </Field>
  <Field label={t('admin.jobRoles.careerField')} error={careerKey ? t(careerKey, { field: t('admin.jobRoles.careerField'), max: 150 }) : formErrors.career_field}>
    <Input bind:value={form.career_field} placeholder="Engineering" />
  </Field>
  <Field label={t('admin.common.description')} error={descKey ? t(descKey, { field: t('admin.common.description'), max: 2000 }) : formErrors.description}>
    <Textarea bind:value={form.description} placeholder="Role summary" />
  </Field>
  <Field label={t('admin.nav.skills')} error={formErrors.skill_ids}>
    <Input bind:value={skillFilter} placeholder={t('admin.jobRoles.searchSkills')} />
    <div class="skill-pick" role="group" aria-label={t('admin.nav.skills')}>
      {#if filteredSkills.length === 0}
        <p class="muted small">{t('admin.jobRoles.noSkills')}</p>
      {:else}
        {#each filteredSkills as s}
          <label class="pick" class:on={selectedIds().includes(s.id)}>
            <input type="checkbox" checked={selectedIds().includes(s.id)} onchange={() => toggleSkill(s.id)} />
            <span>{s.name}</span>
          </label>
        {/each}
      {/if}
    </div>
    <p class="hint">{t('admin.jobRoles.selected', { count: selectedIds().length })}</p>
  </Field>
  {#if Object.keys(formErrors).length}
    <p class="form-err" role="alert">{t('admin.common.checkFields')}</p>
  {/if}
  {#snippet footer()}
    <Button variant="ghost" onclick={() => (showForm = false)} disabled={saving}>{t('common.cancel')}</Button>
    <Button variant="primary" onclick={save} loading={saving} disabled={saving || !dialogValid}>{t('common.save')}</Button>
  {/snippet}
</Dialog>

<Dialog open={showDelete} onclose={() => (showDelete = false)} title={t('admin.jobRoles.delete')}>
  <p>{t('admin.common.deleteConfirm', { name: delTarget?.title })}</p>
  {#if dependents}
    <p class="warn">{t('admin.common.confirmForce', { entity: t('admin.nav.jobRoles') })}</p>
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
  .grid-table { width: 100%; border-collapse: collapse; font-size: 0.92rem; }
  .grid-table th, .grid-table td { text-align: start; padding: 0.6rem 0.5rem; border-bottom: 1px solid var(--line); }
  .grid-table th { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--clay); }
  .actions { display: flex; gap: 0.4rem; justify-content: flex-end; }
  .muted { color: var(--clay); }
  .small { font-size: 0.82rem; }
  .hint { font-size: 0.8rem; color: var(--clay); margin-top: 0.3rem; }
  .skill-pick { display: grid; grid-template-columns: 1fr 1fr; gap: 0.35rem; max-height: 200px; overflow-y: auto; margin-top: 0.5rem; padding: 0.5rem; border: 1px solid var(--line-strong); border-radius: var(--radius); }
  .pick { display: inline-flex; align-items: center; gap: 0.4rem; font-size: 0.88rem; min-height: 36px; padding: 0.25rem 0.4rem; border-radius: var(--radius); cursor: pointer; }
  .pick.on { background: var(--ochre-soft); color: var(--ochre-deep); }
  .form-err { color: var(--danger); font-size: 0.85rem; margin: 0.2rem 0 0; }
  .warn { color: var(--danger); font-size: 0.9rem; }
  .deps { margin: 0.4rem 0 0; padding-inline-start: 1.1rem; font-size: 0.88rem; color: var(--ink-soft); }
  .err-box { background: var(--danger-soft); border: 1px solid var(--danger); color: var(--danger); padding: 1rem; border-radius: var(--radius); display: flex; flex-direction: column; gap: 0.6rem; }
</style>
