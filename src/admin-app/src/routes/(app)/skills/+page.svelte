<!-- Admin skills CRUD: list, create, edit, restricted delete with force. -->
<script lang="ts">
  import { apiFetch, ApiError } from '$lib/api/client';
  import { query } from '$lib/query';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Textarea from '$lib/components/ui/Textarea.svelte';
  import Field from '$lib/components/ui/Field.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Dialog from '$lib/components/ui/Dialog.svelte';
  import { success, error as toastError } from '$lib/components/ui/toast';
  import Icon from '$lib/icons/Icon.svelte';

  let rows = $state<any[]>([]);
  let cats = $state<any[]>([]);
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
      [rows, cats] = await Promise.all([
        query(['SKILLS'], () => apiFetch('/admin/skills')),
        query(['CATS_PICK'], () => apiFetch('/admin/categories'))
      ]);
    } finally { loading = false; }
  }
  $effect(() => { load(); });

  function catOptions() {
    return cats.map((c) => ({ value: c.id, label: c.name }));
  }

  function openCreate() { editing = null; form = {}; showForm = true; }
  function openEdit(r: any) { editing = r; form = { ...r }; showForm = true; }

  async function save() {
    try {
      if (editing) await apiFetch('/admin/skills/' + editing.id, { method: 'PUT', body: form });
      else await apiFetch('/admin/skills', { method: 'POST', body: form });
      success('Saved'); showForm = false; await load();
    } catch (e) {
      toastError(e instanceof ApiError ? e.detail : 'Save failed');
    }
  }

  async function askDelete(r: any) { delTarget = r; dependents = null; showDelete = true; }
  async function doDelete(force: boolean) {
    try {
      await apiFetch('/admin/skills/' + delTarget.id + (force ? '?force=true' : ''), { method: 'DELETE' });
      success('Deleted'); showDelete = false; await load();
    } catch (e) {
      if (e instanceof ApiError && e.status === 409 && e.dependents) dependents = e.dependents;
      else { toastError(e instanceof ApiError ? e.detail : 'Delete failed'); showDelete = false; }
    }
  }
</script>

<h1>Skills</h1>
<Panel title="Skill catalog">
  <div class="toolbar">
    <Button variant="primary" onclick={openCreate}><Icon name="plus" size={16} /> Add skill</Button>
  </div>
  {#if loading}
    <p class="muted">Loading…</p>
  {:else if rows.length === 0}
    <p class="muted">No skills yet.</p>
  {:else}
    <table class="grid-table">
      <thead>
        <tr><th>ID</th><th>Name</th><th>Difficulty</th><th>Hours</th><th>Category</th><th></th></tr>
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
              <Button variant="ghost" size="sm" onclick={() => openEdit(r)}><Icon name="edit" size={15} /> Edit</Button>
              <Button variant="destructive" size="sm" onclick={() => askDelete(r)}><Icon name="trash" size={15} /> Delete</Button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</Panel>

<Dialog open={showForm} onclose={() => (showForm = false)} title={editing ? 'Edit skill' : 'Add skill'}>
  <Field label="Name">
    <Input bind:value={form.name} placeholder="JavaScript Basics" />
  </Field>
  <Field label="Description">
    <Textarea bind:value={form.description} placeholder="What this skill covers" />
  </Field>
  <div class="row">
    <Field label="Difficulty (1-10)">
      <Input bind:value={form.difficulty_level} type="number" min="1" max="10" />
    </Field>
    <Field label="Est. hours">
      <Input bind:value={form.estimated_hours} type="number" min="0" />
    </Field>
  </div>
  <div class="row">
    <Field label="Icon">
      <Input bind:value={form.icon} placeholder="emoji or name" />
    </Field>
    <Field label="Color">
      <Input bind:value={form.color} placeholder="#5b8def" />
    </Field>
  </div>
  <Field label="Category">
    <Select bind:value={form.category_id} options={catOptions()} placeholder="None" />
  </Field>
  {#snippet footer()}
    <Button variant="ghost" onclick={() => (showForm = false)}>Cancel</Button>
    <Button variant="primary" onclick={save}>Save</Button>
  {/snippet}
</Dialog>

<Dialog open={showDelete} onclose={() => (showDelete = false)} title="Delete skill">
  <p>Delete <strong>{delTarget?.name}</strong>? This cannot be undone.</p>
  {#if dependents}
    <p class="warn">This skill still has related records. Force delete to remove them:</p>
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
  .row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; }
  .grid-table { width: 100%; border-collapse: collapse; font-size: 0.92rem; }
  .grid-table th, .grid-table td { text-align: left; padding: 0.6rem 0.5rem; border-bottom: 1px solid var(--line); }
  .grid-table th { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); }
  .actions { display: flex; gap: 0.4rem; justify-content: flex-end; }
  .muted { color: var(--muted); }
  .warn { color: var(--danger); font-size: 0.9rem; }
  .deps { margin: 0.4rem 0 0; padding-left: 1.1rem; font-size: 0.88rem; color: var(--ink-soft); }
</style>
