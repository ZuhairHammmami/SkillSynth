<!-- Path detail: step completion toggles, progress, and delete (force on 409). -->
<script lang="ts">
  import { page } from '$app/stores';
  import { apiFetch, ApiError } from '$lib/api/client';
  import { query, invalidate } from '$lib/query';
  import { goto } from '$app/navigation';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Dialog from '$lib/components/ui/Dialog.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Icon from '$lib/icons/Icon.svelte';
  import ProgressMeter from '$lib/components/ProgressMeter.svelte';
  import { success, error as toastError, info } from '$lib/components/ui/toast';
  import TakeQuizDialog from '$lib/components/TakeQuizDialog.svelte';
  import { t } from '$lib/i18n';

  const id = $derived($page.params.id ?? '');
  let path = $state<any>(null);
  let loading = $state(true);
  let busyStep = $state<number | null>(null);
  let showDelete = $state(false);
  let dependents = $state<Record<string, number> | null>(null);
  let showQuiz = $state(false);
  let skills = $derived((path?.steps ?? []).map((s: any) => s.skill).filter((s: any) => s && s.id).map((s: any) => ({ id: s.id, name: s.name })));

  async function load() {
    loading = true;
    try { path = await query(['path', id], () => apiFetch('/paths/' + id)); }
    catch { path = null; }
    finally { loading = false; }
  }
  $effect(() => { id; load(); });

  async function toggle(step: any) {
    busyStep = step.id;
    try {
      const ep = step.completed ? '/undo-complete' : '/complete';
      await apiFetch(`/steps/${step.id}${ep}`, { method: 'POST' });
      await invalidate(['path', id]);
      await invalidate(['dashboard']);
      await load();
    } catch (e) {
      toastError(e instanceof ApiError ? e.detail : 'Update failed');
    } finally {
      busyStep = null;
    }
  }

  async function doDelete(force: boolean) {
    try {
      await apiFetch('/paths/' + id + (force ? '?force=true' : ''), { method: 'DELETE' });
      success('Path deleted');
      await invalidate(['paths']);
      goto('/learn');
    } catch (e) {
      if (e instanceof ApiError && e.status === 409 && e.dependents) {
        dependents = e.dependents;
        showDelete = true;
      } else {
        toastError(e instanceof ApiError ? e.detail : 'Delete failed');
      }
    }
  }
</script>

{#if loading}
  <div class="center-spin"><Spinner /></div>
{:else if !path}
  <Panel><p class="muted">{t('pathDetailPage.notFound')}</p></Panel>
{:else}
  <div class="head between">
    <div>
      <h1>{path.title}</h1>
      <Badge tone="ochre">{path.goal}</Badge>
    </div>
    <Button variant="destructive" onclick={() => doDelete(false)}><Icon name="trash" size={16} />{t('pathDetailPage.deleteConfirm')}</Button>
    <Button onclick={() => (showQuiz = true)}><Icon name="sparkles" size={16} />{t('wizard.assessmentTitle')}</Button>
  </div>

  <div class="stats">
    <Panel title={t('pathDetailPage.progress')}><ProgressMeter value={path.progress ?? 0} /></Panel>
    <Panel title={t('pathDetailPage.duration')}><div class="big">{Math.round((path.steps ?? []).reduce((a: number, s: any) => a + (s.duration_hours ?? 0), 0))}h</div></Panel>
    <Panel title={t('pathDetailPage.skillsTitle')}><div class="big">{(path.steps ?? []).length}</div></Panel>
  </div>

  <h2 class="section-title">{t('pathDetailPage.stepsTitle')}</h2>
  <ol class="steps">
    {#each (path.steps ?? []).slice().sort((a: any, b: any) => (a.order_index ?? 0) - (b.order_index ?? 0)) as step}
      <li class:done={step.completed}>
        <button class="toggle" onclick={() => toggle(step)} disabled={busyStep === step.id}>
          {#if busyStep === step.id}<Spinner />{:else if step.completed}<Icon name="check" size={16} />{:else}<Icon name="plus" size={16} />{/if}
        </button>
        <div class="body">
          <strong>{step.title}</strong>
          {#if step.description}<p class="muted">{step.description}</p>{/if}
          <small class="muted">{step.duration_hours ?? 0}h · {step.skill?.name ?? ''}</small>
        </div>
      </li>
    {/each}
  </ol>
{/if}

<Dialog bind:open={showDelete} title={t('pathDetailPage.deleteConfirm')}>
  <p>{t('pathDetailPage.deleteConfirm')}?</p>
  {#if dependents}
    <ul class="dep">
      {#each Object.entries(dependents) as [table, count]}<li>{count} × {table}</li>{/each}
    </ul>
  {/if}
  {#snippet footer()}
    <Button variant="ghost" onclick={() => (showDelete = false)}>{t('common.cancel')}</Button>
    <Button variant="destructive" onclick={() => doDelete(true)}>{t('common.forceDelete')}</Button>
  {/snippet}
</Dialog>

<TakeQuizDialog bind:open={showQuiz} {skills} />

<style>
  .center-spin { display: flex; justify-content: center; padding: 3rem; }
  .head { margin-bottom: 1.2rem; }
  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
  .big { font-family: var(--font-display); font-size: 1.8rem; color: var(--ochre-deep); }
  .section-title { margin-top: 2rem; font-size: 1.3rem; }
  .steps { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.6rem; }
  .steps li { display: flex; gap: 0.8rem; align-items: flex-start; padding: 0.8rem; border: 1px solid var(--line); border-radius: var(--radius); background: var(--paper); }
  .steps li.done { border-inline-start: 3px solid var(--sage); }
  .toggle { flex-shrink: 0; width: 32px; height: 32px; border-radius: 50%; border: 1px solid var(--line-strong); background: var(--paper-2); cursor: pointer; display: inline-flex; align-items: center; justify-content: center; color: var(--ochre-deep); }
  .toggle:disabled { opacity: 0.6; }
  .body { display: flex; flex-direction: column; gap: 0.2rem; }
  .dep { margin: 0.5rem 0 0; padding-inline-start: 1.2rem; color: var(--danger); }
</style>
