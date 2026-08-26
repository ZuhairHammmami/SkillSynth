<!-- Admin users CRUD: list, create, edit, restricted delete with force. -->
<script lang="ts">
  import { apiFetch, ApiError } from '$lib/api/client';
  import { query } from '$lib/query';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Field from '$lib/components/ui/Field.svelte';
  import Dialog from '$lib/components/ui/Dialog.svelte';
  import { success, error as toastError } from '$lib/components/ui/toast';
  import Icon from '$lib/icons/Icon.svelte';

  let rows = $state<any[]>([]);
  let loading = $state(true);
  let showForm = $state(false);
  let editing = $state<any>(null);
  let form = $state<any>({});
  let showDelete = $state(false);
  let delTarget = $state<any>(null);
  let dependents = $state<Record<string, number> | null>(null);

  async function load() {
    loading = true;
    try { rows = await query(['USERS'], () => apiFetch('/admin/users')); }
    finally { loading = false; }
  }
  $effect(() => { load(); });

  function openCreate() { editing = null; form = { is_admin: false }; showForm = true; }
  function openEdit(r: any) { editing = r; form = { ...r }; showForm = true; }

  async function save() {
    try {
      if (editing) await apiFetch('/admin/users/' + editing.id, { method: 'PUT', body: form });
      else await apiFetch('/admin/users', { method: 'POST', body: form });
      success('Saved'); showForm = false; await load();
    } catch (e) {
      toastError(e instanceof ApiError ? e.detail : 'Save failed');
    }
  }

  async function askDelete(r: any) { delTarget = r; dependents = null; showDelete = true; }
  async function doDelete(force: boolean) {
    try {
      await apiFetch('/admin/users/' + delTarget.id + (force ? '?force=true' : ''), { method: 'DELETE' });
      success('Deleted'); showDelete = false; await load();
    } catch (e) {
      if (e instanceof ApiError && e.status === 409 && e.dependents) dependents = e.dependents;
      else { toastError(e instanceof ApiError ? e.detail : 'Delete failed'); showDelete = false; }
    }
  }
</script>

<h1>Users</h1>
<Panel title="Platform users">
  <div class="toolbar">
    <Button variant="primary" onclick={openCreate}><Icon name="plus" size={16} /> Add user</Button>
  </div>
  {#if loading}
    <p class="muted">Loading…</p>
  {:else if rows.length === 0}
    <p class="muted">No users yet.</p>
  {:else}
    <table class="grid-table">
      <thead>
        <tr><th>ID</th><th>Email</th><th>Name</th><th>Admin</th><th></th></tr>
      </thead>
      <tbody>
        {#each rows as r (r.id)}
          <tr>
            <td>{r.id}</td>
            <td>{r.email}</td>
            <td>{r.full_name ?? '—'}</td>
            <td>{r.is_admin ? 'Yes' : 'No'}</td>
            <td class="actions">
              <Button variant="ghost" size="sm" onclick={() => openEdit(r)}><Icon name="edit" size={15} /> Edit</Button>
              <Button variant="destructive" size="sm" onclick={() => askDelete(r)}><Icon name="trash" size={15} /> Delete</Button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</Panel>

<Dialog open={showForm} onclose={() => (showForm = false)} title={editing ? 'Edit user' : 'Add user'}>
  <Field label="Email">
    <Input bind:value={form.email} type="email" placeholder="user@example.com" />
  </Field>
  <Field label="Full name">
    <Input bind:value={form.full_name} placeholder="Jane Doe" />
  </Field>
  <Field label={editing ? 'Password (leave blank to keep)' : 'Password'}>
    <Input bind:value={form.password} type="password" placeholder="••••••" />
  </Field>
  <Field label="Admin">
    <label class="check"><input type="checkbox" bind:checked={form.is_admin} /> Grant admin access</label>
  </Field>
  {#snippet footer()}
    <Button variant="ghost" onclick={() => (showForm = false)}>Cancel</Button>
    <Button variant="primary" onclick={save}>Save</Button>
  {/snippet}
</Dialog>

<Dialog open={showDelete} onclose={() => (showDelete = false)} title="Delete user">
  <p>Delete <strong>{delTarget?.email}</strong>? This cannot be undone.</p>
  {#if dependents}
    <p class="warn">This user still has related records. Force delete to remove them:</p>
    <ul class="deps">
      {#each Object.entries(dependents) as [k, v]}
        <li>{k}: {v}</li>
      {/each}
    </ul>
  {/if}
  {#snippet footer()}
    <Button variant="ghost" onclick={() => (showDelete = false)}>Cancel</Button>
    {#if dependents}
      <Button variant="destructive" onclick={() => doDelete(true)}>Force delete</Button>
    {:else}
      <Button variant="destructive" onclick={() => doDelete(false)}>Delete</Button>
    {/if}
  {/snippet}
</Dialog>

<style>
  .toolbar { display: flex; justify-content: flex-end; margin-bottom: 1rem; }
  .grid-table { width: 100%; border-collapse: collapse; font-size: 0.92rem; }
  .grid-table th, .grid-table td { text-align: left; padding: 0.6rem 0.5rem; border-bottom: 1px solid var(--line); }
  .grid-table th { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); }
  .actions { display: flex; gap: 0.4rem; justify-content: flex-end; }
  .muted { color: var(--muted); }
  .check { display: inline-flex; align-items: center; gap: 0.5rem; font-size: 0.92rem; }
  .warn { color: var(--danger); font-size: 0.9rem; }
  .deps { margin: 0.4rem 0 0; padding-left: 1.1rem; font-size: 0.88rem; color: var(--ink-soft); }
</style>
