<!-- Learn: list of the user's paths with a New Path entry to the wizard. -->
<script lang="ts">
  import { apiFetch, ApiError } from '$lib/api/client';
  import { query, invalidate } from '$lib/query';
  import { goto } from '$app/navigation';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Illustration from '$lib/components/Illustration.svelte';
  import PathCard from '$lib/components/PathCard.svelte';
  import Icon from '$lib/icons/Icon.svelte';
  import { error as toastError } from '$lib/components/ui/toast';
  import { t } from '$lib/i18n';

  let paths = $state<any[]>([]);
  let loading = $state(true);
  let loadError = $state('');
  async function load() {
    loading = true;
    loadError = '';
    try { paths = (await query(['paths'], () => apiFetch('/paths/'))).items ?? []; }
    catch (e) {
      loadError = e instanceof ApiError ? e.detail : 'Failed to load paths';
      toastError(loadError);
    }
    finally { loading = false; }
  }
  $effect(() => {
    load();
    const h = () => { invalidate(['paths']); load(); };
    window.addEventListener('sse:path_generated', h);
    return () => window.removeEventListener('sse:path_generated', h);
  });
</script>

<div class="between">
  <div>
    <h1>{t('learnPage.title')}</h1>
    <p class="muted">{t('learnPage.subtitle')}</p>
  </div>
  <Button onclick={() => goto('/wizard')}><Icon name="plus" size={16} />{t('dashboardPage.newPath')}</Button>
</div>

{#if loading}
  <div class="center-spin"><Spinner /></div>
{:else if loadError}
  <Panel>
    <div class="err-state">
      <Icon name="alert" size={22} />
      <p>{t('learnPage.errorLoading')}</p>
      <Button onclick={load}>{t('common.retry')}</Button>
    </div>
  </Panel>
{:else if paths.length === 0}
  <Panel class="empty">
    <Illustration name="empty" width={160} />
    <h3>{t('learnPage.emptyTitle')}</h3>
    <p class="muted">{t('learnPage.emptyDesc')}</p>
    <Button onclick={() => goto('/wizard')}>{t('dashboardPage.newPath')}</Button>
  </Panel>
{:else}
  <div class="cards">
    {#each paths as p}<PathCard path={p} />{/each}
  </div>
{/if}

<style>
  .between { display: flex; align-items: flex-end; justify-content: space-between; gap: 1rem; margin-bottom: 1.5rem; }
  .center-spin { display: flex; justify-content: center; padding: 3rem; }
  .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1rem; }
  .err-state { display: flex; flex-direction: column; align-items: flex-start; gap: 0.6rem; color: var(--danger); }
</style>
