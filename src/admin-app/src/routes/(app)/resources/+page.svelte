<!-- Admin resources CRUD: list, create, edit, restricted delete with force. -->
<script lang="ts">
  import { apiFetch, ApiError, fieldErrorsFrom } from '$lib/api/client';
  import { query, invalidate } from '$lib/query';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Field from '$lib/components/ui/Field.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Dialog from '$lib/components/ui/Dialog.svelte';
  import { success, error as toastError } from '$lib/components/ui/toast';
  import Icon from '$lib/icons/Icon.svelte';
  import { t } from '$lib/i18n';
  import { name, maxLength, url, positiveInt } from '$lib/validation';

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
  let touched = $state<Record<string, boolean>>({});

  // Live client-side dialog validity (T16); server 422 fieldErrors stay
  // authority. The URL is required (backend Field(...)) plus http(s); the
  // linked-skill FK is optional so positiveInt only runs when selected.
  const titleErr = $derived(name(String(form.title ?? '')));
  const urlErr = $derived((form.url ?? '').trim() ? url(String(form.url)) : 'admin.validation.required');
  const authorErr = $derived(maxLength(String(form.author_or_platform ?? ''), 150));
  const langErr = $derived(maxLength(String(form.language ?? ''), 150));
  const skillErr = $derived(form.skill_id != null && form.skill_id !== '' ? positiveInt(form.skill_id) : null);
  const titleKey = $derived(touched.title || (form.title ?? '') ? titleErr : null);
  const urlKey = $derived(touched.url || (form.url ?? '').trim() ? urlErr : null);
  const authorKey = $derived((form.author_or_platform ?? '') ? authorErr : null);
  const langKey = $derived((form.language ?? '') ? langErr : null);
  const skillKey = $derived(form.skill_id != null && form.skill_id !== '' ? skillErr : null);
  const dialogValid = $derived(titleErr === null && urlErr === null && authorErr === null && langErr === null && skillErr === null);

  async function load() {
    loading = true;
    err = null;
    try {
      [rows, skills] = await Promise.all([
        query(['RESOURCES'], () => apiFetch('/admin/resources')),
        query(['SKILLS_PICK'], () => apiFetch('/admin/skills'))
      ]);
    } catch (e) { err = e instanceof ApiError ? e.detail : t('admin.common.failedLoad', { entity: t('admin.nav.resources') }); }
    finally { loading = false; }
  }
  $effect(() => { load(); });

  function skillOptions() {
    return skills.map((s) => ({ value: s.id, label: s.name }));
  }

  function openCreate() { editing = null; formErrors = {}; touched = {}; form = { is_free: true, is_official: false, language: 'en' }; showForm = true; }
  function openEdit(r: any) { editing = r; formErrors = {}; touched = {}; form = { ...r }; showForm = true; }

  async function save() {
    formErrors = {};
    saving = true;
    try {
      if (editing) await apiFetch('/admin/resources/' + editing.id, { method: 'PUT', body: form });
      else await apiFetch('/admin/resources', { method: 'POST', body: form });
      success(t('admin.common.saved')); showForm = false;
      invalidate(['RESOURCES']); invalidate(['SKILLS_PICK']); await load();
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
      await apiFetch('/admin/resources/' + delTarget.id + (force ? '?force=true' : ''), { method: 'DELETE' });
      success(t('admin.common.deleted')); showDelete = false;
      invalidate(['RESOURCES']); invalidate(['SKILLS_PICK']); await load();
    } catch (e) {
      if (e instanceof ApiError && e.status === 409 && e.dependents) dependents = e.dependents;
      else { toastError(e instanceof ApiError ? e.detail : t('admin.common.deleteFailed')); showDelete = false; }
    } finally { deleting = false; }
  }
</script>

<h1>{t('admin.resources.title')}</h1>
<Panel title={t('admin.resources.panel')}>
  <div class="toolbar">
    <Button variant="primary" onclick={openCreate}><Icon name="plus" size={16} /> {t('admin.resources.add')}</Button>
  </div>

  {#if loading}
    <p class="muted">{t('common.loading')}</p>
  {:else if err}
    <div class="err-box" role="alert">
      <p>{err}</p>
      <Button variant="ghost" onclick={load}><Icon name="refresh" size={15} /> {t('common.retry')}</Button>
    </div>
  {:else if rows.length === 0}
    <p class="muted">{t('admin.resources.empty')}</p>
  {:else}
    <div class="table-scroll">
      <table class="grid-table">
        <thead>
          <tr><th>{t('admin.common.id')}</th><th>{t('admin.common.title')}</th><th>{t('admin.common.type')}</th><th>{t('admin.common.language')}</th><th>{t('admin.resources.free')}</th><th>{t('admin.resources.official')}</th><th>{t('admin.common.skill')}</th><th></th></tr>
        </thead>
        <tbody>
          {#each rows as r (r.id)}
            <tr>
              <td>{r.id}</td>
              <td><a class="link" href={r.url} target="_blank" rel="noreferrer">{r.title}</a></td>
              <td>{r.type}</td>
              <td>{r.language}</td>
              <td>{r.is_free ? t('admin.common.yes') : t('admin.common.no')}</td>
              <td>{r.is_official ? t('admin.common.yes') : t('admin.common.no')}</td>
              <td>{r.skill_id ?? '—'}</td>
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

<Dialog open={showForm} onclose={() => (showForm = false)} title={editing ? t('admin.resources.edit') : t('admin.resources.add')}>
  <Field label={t('admin.resources.fieldTitle')} error={titleKey ? t(titleKey, { field: t('admin.resources.fieldTitle'), max: 100 }) : formErrors.title}>
    <Input bind:value={form.title} placeholder="MDN Web Docs" onblur={() => (touched.title = true)} />
  </Field>
  <Field label={t('admin.resources.url')} error={urlKey ? t(urlKey, { field: t('admin.resources.url') }) : formErrors.url}>
    <Input bind:value={form.url} type="url" placeholder="https://example.com" onblur={() => (touched.url = true)} />
  </Field>
  <div class="row">
    <Field label={t('admin.common.type')} error={formErrors.type}>
      <Input bind:value={form.type} placeholder="article, video, course…" />
    </Field>
    <Field label={t('admin.common.language')} error={langKey ? t(langKey, { field: t('admin.common.language'), max: 150 }) : formErrors.language}>
      <Input bind:value={form.language} placeholder="en" />
    </Field>
  </div>
  <Field label={t('admin.resources.author')} error={authorKey ? t(authorKey, { field: t('admin.resources.author'), max: 150 }) : formErrors.author_or_platform}>
    <Input bind:value={form.author_or_platform} placeholder="Mozilla" />
  </Field>
  <Field label={t('admin.resources.linkedSkill')} error={skillKey ? t(skillKey, { field: t('admin.resources.linkedSkill') }) : formErrors.skill_id}>
    <Select bind:value={form.skill_id} options={skillOptions()} placeholder="None" />
  </Field>
  <div class="checks">
    <label class="check"><input type="checkbox" bind:checked={form.is_free} /> {t('admin.resources.free')}</label>
    <label class="check"><input type="checkbox" bind:checked={form.is_official} /> {t('admin.resources.official')}</label>
  </div>
  {#if Object.keys(formErrors).length}
    <p class="form-err" role="alert">{t('admin.common.checkFields')}</p>
  {/if}
  {#snippet footer()}
    <Button variant="ghost" onclick={() => (showForm = false)} disabled={saving}>{t('common.cancel')}</Button>
    <Button variant="primary" onclick={save} loading={saving} disabled={saving || !dialogValid}>{t('common.save')}</Button>
  {/snippet}
</Dialog>

<Dialog open={showDelete} onclose={() => (showDelete = false)} title={t('admin.resources.delete')}>
  <p>{t('admin.common.deleteConfirm', { name: delTarget?.title })}</p>
  {#if dependents}
    <p class="warn">{t('admin.common.confirmForce', { entity: t('admin.nav.resources') })}</p>
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
  .checks { display: flex; gap: 1.2rem; margin-top: 0.4rem; }
  .check { display: inline-flex; align-items: center; gap: 0.5rem; font-size: 0.92rem; min-height: 44px; }
  .grid-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
  .grid-table th, .grid-table td { text-align: start; padding: 0.6rem 0.5rem; border-bottom: 1px solid var(--line); }
  .grid-table th { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--clay); }
  .grid-table a.link { color: var(--ochre-deep); text-decoration: none; }
  .grid-table a.link:hover { text-decoration: underline; }
  .actions { display: flex; gap: 0.4rem; justify-content: flex-end; }
  .muted { color: var(--clay); }
  .warn { color: var(--danger); font-size: 0.9rem; }
  .deps { margin: 0.4rem 0 0; padding-inline-start: 1.1rem; font-size: 0.88rem; color: var(--ink-soft); }
  .form-err { color: var(--danger); font-size: 0.85rem; margin: 0.2rem 0 0; }
  .err-box { background: var(--danger-soft); border: 1px solid var(--danger); color: var(--danger); padding: 1rem; border-radius: var(--radius); display: flex; flex-direction: column; gap: 0.6rem; }
</style>
