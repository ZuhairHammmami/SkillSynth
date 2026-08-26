<!-- Admin job-roles CRUD: list, create, edit, restricted delete with force. -->
<script lang="ts">
  import { apiFetch, ApiError } from '$lib/api/client';
  import { query } from '$lib/query';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Textarea from '$lib/components/ui/Textarea.svelte';
  import Field from '$lib/components/ui/Field.svelte';
  import Dialog from '$lib/components/ui/Dialog.svelte';
  import { success, error as toastError } from '$lib/components/ui/toast';
  import Icon from '$lib/icons/Icon.svelte';

  let rows = $state<any[]>([]);
  let skills = $state<any[]>([]);
  let loading = $state(true);
  let showForm = $state(false);
  let editing = $state<any>(null);
  let form = $state<any>({});
  let showDelete = $state(false);
  let delTarget = $state<any>(null);
  let dependents = $state<Record<string, number> | null>(null);

  async function load() {
    loading = true;
    try {
      [rows, skills] = await Promise.all([
        query(['ROLES'], () => apiFetch('/admin/job-roles')),
        query(['SKILLS_PICK_ROLES'], () => apiFetch('/admin/skills'))
      ]);
    } finally { loading = false; }
  }
  $effect(() => { load(); });

  function idsString(ids: any): string {
    if (!ids) return '';
    if (Array.isArray(ids)) return ids.join(', ');
    return String(ids);
  }

  function skillHint(): string {
    return skills.map((s) => s.id + '=' + s.name).join(', ');
  }

  function parseIds(s: any): number[] {
    if (Array.isArray(s)) return s.map(Number).filter((n) => Number.isFinite(n) && n > 0);
    return String(s ?? '')
      .split(',')
      .map((x) => parseInt(x.trim(), 10))
      .filter((n) => Number.isFinite(n) && n > 0);
  }

  function openCreate() { editing = null; form = { skill_ids: '' }; showForm = true; }
  function openEdit(r: any) { editing = r; form = { ...r, skill_ids: idsString(r.skill_ids) }; showForm = true; }

  async function save() {
    const payload = { ...form, skill_ids: parseIds(form.skill_ids) };
    try {
      if (editing) await apiFetch('/admin/job-roles/' + editing.id, { method: 'PUT', body: payload });
      else await apiFetch('/admin/job-roles', { method: 'POST', body: payload });
      success('Saved'); showForm = false; await load();
    } catch (e) {
      toastError(e instanceof ApiError ? e.detail : 'Save failed');
    }
  }

  async function askDelete(r: any) { delTarget = r; dependents = null; showDelete = true; }
  async function doDelete(force: boolean) {
    try {
      await apiFetch('/admin/job-roles/' + delTarget.id + (force ? '?force=true' : ''), { method: 'DELETE' });
      success('Deleted'); showDelete = false; await load();
    } catch (e) {
      if (e instanceof ApiError && e.status === 409 && e.dependents) dependents = e.dependents;
      else { toastError(e instanceof ApiError ? e.detail : 'Delete failed'); showDelete = false; }
    }
  }
</script>

<h1>Job Roles</h1>
<Panel title="Career roles">
  <div class="toolbar">
    <Button variant="primary" onclick={openCreate}><Icon name="plus" size={16} /> Add job role</Button>
  </div>
  {#if loading}
    <p class="muted">Loading…</p>
  {:else if rows.length === 0}
    <p class="muted">No job roles yet.</p>
  {:else}
    <table class="grid-table">
      <thead>
        <tr><th>ID</th><th>Title</th><th>Career field</th><th>Skills</th><th></th></tr>
      </thead>
      <tbody>
        {#each rows as r (r.id)}
          <tr>
            <td>{r.id}</td>
            <td>{r.title}</td>
            <td>{r.career_field ?? '—'}</td>
            <td>{(r.skill_ids ?? []).length}</td>
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

<Dialog open={showForm} onclose={() => (showForm = false)} title={editing ? 'Edit job role' : 'Add job role'}>
  <Field label="Title">
    <Input bind:value={form.title} placeholder="Frontend Engineer" />
  </Field>
  <Field label="Career field">
    <Input bind:value={form.career_field} placeholder="Engineering" />
  </Field>
  <Field label="Description">
    <Textarea bind:value={form.description} placeholder="Role summary" />
  </Field>
  <Field label="Skill IDs (comma-separated)">
    <Input bind:value={form.skill_ids} placeholder="1, 4, 7" />
  </Field>
  <p class="hint">Available: {skillHint()}</p>
  {#snippet footer()}
    <Button variant="ghost" onclick={() => (showForm = false)}>Cancel</Button>
    <Button variant="primary" onclick={save}>Save</Button>
  {/snippet}
</Dialog>

<Dialog open={showDelete} onclose={() => (showDelete = false)} title="Delete job role">
  <p>Delete <strong>{delTarget?.title}</strong>? This cannot be undone.</p>
  {#if dependents}
    <p class="warn">This job role still has related records. Force delete to remove them:</p>
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
  .hint { font-size: 0.8rem; color: var(--muted); margin-top: 0.3rem; }
  .warn { color: var(--danger); font-size: 0.9rem; }
  .deps { margin: 0.4rem 0 0; padding-left: 1.1rem; font-size: 0.88rem; color: var(--ink-soft); }
</style>
