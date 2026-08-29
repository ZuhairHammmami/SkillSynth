<!-- Admin users CRUD: list, create, edit, restricted delete with force. -->
<script lang="ts">
  import { apiFetch, ApiError, fieldErrorsFrom } from '$lib/api/client';
  import { query, invalidate } from '$lib/query';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Field from '$lib/components/ui/Field.svelte';
  import Dialog from '$lib/components/ui/Dialog.svelte';
  import { success, error as toastError } from '$lib/components/ui/toast';
  import Icon from '$lib/icons/Icon.svelte';
  import { t } from '$lib/i18n';
  import { email, name, password as validatePw, DEFAULT_PASSWORD_POLICY } from '$lib/validation';

  let rows = $state<any[]>([]);
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

  // Live client-side dialog validity (T16); server 422 fieldErrors stay authority.
  // Password is required ONLY on create; the edit field is "leave blank to keep",
  // so policy checks apply only when a new value is typed.
  const emailErr = $derived(email(String(form.email ?? '')));
  const nameErr = $derived((form.full_name ?? '').trim() ? name(String(form.full_name)) : null);
  const pwErr = $derived(
    editing ? ((form.password ?? '') ? validatePw(String(form.password)) : null)
            : validatePw(String(form.password ?? ''))
  );
  const emailKey = $derived(touched.email || (form.email ?? '') ? emailErr : null);
  const nameKey = $derived(touched.full_name || (form.full_name ?? '').trim() ? nameErr : null);
  const pwKey = $derived(
    editing ? ((form.password ?? '') ? pwErr : null)
            : (touched.password || (form.password ?? '') ? pwErr : null)
  );
  const dialogValid = $derived(emailErr === null && nameErr === null && pwErr === null);

  async function load() {
    loading = true;
    err = null;
    try { rows = await query(['USERS'], () => apiFetch('/admin/users')); }
    catch (e) { err = e instanceof ApiError ? e.detail : t('admin.common.failedLoad', { entity: t('admin.nav.users') }); }
    finally { loading = false; }
  }
  $effect(() => { load(); });

  function openCreate() { editing = null; formErrors = {}; touched = {}; form = { is_admin: false }; showForm = true; }
  function openEdit(r: any) { editing = r; formErrors = {}; touched = {}; form = { ...r }; showForm = true; }

  async function save() {
    formErrors = {};
    saving = true;
    try {
      if (editing) await apiFetch('/admin/users/' + editing.id, { method: 'PUT', body: form });
      else await apiFetch('/admin/users', { method: 'POST', body: form });
      success(t('admin.common.saved')); showForm = false;
      invalidate(['USERS']); await load();
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
      await apiFetch('/admin/users/' + delTarget.id + (force ? '?force=true' : ''), { method: 'DELETE' });
      success(t('admin.common.deleted')); showDelete = false;
      invalidate(['USERS']); await load();
    } catch (e) {
      if (e instanceof ApiError && e.status === 409 && e.dependents) dependents = e.dependents;
      else { toastError(e instanceof ApiError ? e.detail : t('admin.common.deleteFailed')); showDelete = false; }
    } finally { deleting = false; }
  }
</script>

<h1>{t('admin.users.title')}</h1>
<Panel title={t('admin.users.panel')}>
  <div class="toolbar">
    <Button variant="primary" onclick={openCreate}><Icon name="plus" size={16} /> {t('admin.users.add')}</Button>
  </div>

  {#if loading}
    <p class="muted">{t('common.loading')}</p>
  {:else if err}
    <div class="err-box" role="alert">
      <p>{err}</p>
      <Button variant="ghost" onclick={load}><Icon name="refresh" size={15} /> {t('common.retry')}</Button>
    </div>
  {:else if rows.length === 0}
    <p class="muted">{t('admin.users.empty')}</p>
  {:else}
    <div class="table-scroll">
      <table class="grid-table">
        <thead>
          <tr><th>{t('admin.common.id')}</th><th>{t('admin.common.email')}</th><th>{t('admin.common.name')}</th><th>{t('admin.common.admin')}</th><th></th></tr>
        </thead>
        <tbody>
          {#each rows as r (r.id)}
            <tr>
              <td>{r.id}</td>
              <td>{r.email}</td>
              <td>{r.full_name ?? '—'}</td>
              <td>{r.is_admin ? t('admin.common.yes') : t('admin.common.no')}</td>
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

<Dialog open={showForm} onclose={() => (showForm = false)} title={editing ? t('admin.users.edit') : t('admin.users.add')}>
  <Field label={t('admin.common.email')} error={emailKey ? t(emailKey, { field: t('admin.common.email') }) : formErrors.email}>
    <Input bind:value={form.email} type="email" placeholder="user@example.com" onblur={() => (touched.email = true)} />
  </Field>
  <Field label={t('admin.users.fullName')} error={nameKey ? t(nameKey, { field: t('admin.users.fullName'), max: 100 }) : formErrors.full_name}>
    <Input bind:value={form.full_name} placeholder="Jane Doe" onblur={() => (touched.full_name = true)} />
  </Field>
  <Field label={editing ? t('admin.users.passwordEdit') : t('admin.common.password')} error={pwKey ? t(pwKey, { field: editing ? t('admin.users.passwordEdit') : t('admin.common.password'), min: DEFAULT_PASSWORD_POLICY.min_length, max: 32 }) : formErrors.password}>
    <Input bind:value={form.password} type="password" placeholder="••••••" hint={editing ? '' : t('registerPage.passwordHint')} onblur={() => (touched.password = true)} />
  </Field>
  <Field label={t('admin.common.admin')}>
    <label class="check"><input type="checkbox" bind:checked={form.is_admin} /> {t('admin.users.grantAdmin')}</label>
  </Field>
  {#if Object.keys(formErrors).length}
    <p class="form-err" role="alert">{t('admin.common.checkFields')}</p>
  {/if}
  {#snippet footer()}
    <Button variant="ghost" onclick={() => (showForm = false)} disabled={saving}>{t('common.cancel')}</Button>
    <Button variant="primary" onclick={save} loading={saving} disabled={saving || !dialogValid}>{t('common.save')}</Button>
  {/snippet}
</Dialog>

<Dialog open={showDelete} onclose={() => (showDelete = false)} title={t('admin.users.delete')}>
  <p>{t('admin.common.deleteConfirm', { name: delTarget?.email })}</p>
  {#if dependents}
    <p class="warn">{t('admin.common.confirmForce', { entity: t('admin.nav.users') })}</p>
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
  .check { display: inline-flex; align-items: center; gap: 0.5rem; font-size: 0.92rem; min-height: 44px; }
  .warn { color: var(--danger); font-size: 0.9rem; }
  .deps { margin: 0.4rem 0 0; padding-inline-start: 1.1rem; font-size: 0.88rem; color: var(--ink-soft); }
  .form-err { color: var(--danger); font-size: 0.85rem; margin: 0.2rem 0 0; }
  .err-box { background: var(--danger-soft); border: 1px solid var(--danger); color: var(--danger); padding: 1rem; border-radius: var(--radius); display: flex; flex-direction: column; gap: 0.6rem; }
</style>
