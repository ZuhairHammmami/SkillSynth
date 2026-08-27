<!-- Learner catalog browse: categories grid and drill-down to skills. -->
<script lang="ts">
  import { apiFetch, ApiError } from '$lib/api/client';
  import { query } from '$lib/query';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Icon from '$lib/icons/Icon.svelte';
  import { error as toastError } from '$lib/components/ui/toast';
  import { t } from '$lib/i18n';

  let categories = $state<any[]>([]);
  let progress = $state<any>(null);
  let selected = $state<any | null>(null);
  let loading = $state(true);

  const catProgress = (id: number) =>
    progress?.categories?.find((p: any) => p.category_id === id)?.completion_percentage ?? 0;

  async function load() {
    loading = true;
    try {
      categories = await query(['catalog', 'categories'], () => apiFetch('/catalog/categories'));
      progress = await query(['analytics', 'progress-by-category'], () =>
        apiFetch('/analytics/progress-by-category')
      );
    } catch (e) {
      toastError(e instanceof ApiError ? e.detail : t('analytics.noData'));
    } finally {
      loading = false;
    }
  }

  $effect(() => {
    load();
  });
</script>

{#if loading}
  <div class="center-spin"><Spinner /></div>
{:else if selected}
  <div class="head between">
    <div>
      <h1>{selected.name}</h1>
      {#if selected.description}<p class="muted">{selected.description}</p>{/if}
    </div>
    <Button variant="ghost" onclick={() => (selected = null)}>
      <Icon name="chevron" size={16} />{t('catalog.backToCategories')}
    </Button>
  </div>

  <h2 class="section-title">{t('catalog.skills')}</h2>
  {#if (selected.skills ?? []).length === 0}
    <Panel><p class="muted">{t('catalog.emptySkills')}</p></Panel>
  {:else}
    <div class="skills">
      {#each selected.skills as skill}
        <Panel>
          <div class="skill-head">
            <strong>{skill.name}</strong>
            {#if skill.difficulty_level}
              <Badge tone="accent">{t('catalog.level')}: {skill.difficulty_level}</Badge>
            {/if}
          </div>
          {#if skill.description}<p class="muted">{skill.description}</p>{/if}
          <small class="muted">
            {skill.estimated_hours ?? 0}h
            {#if skill.icon} · {skill.icon}{/if}
          </small>
        </Panel>
      {/each}
    </div>
  {/if}
{:else}
  <div class="head">
    <div>
      <h1>{t('catalog.browse')}</h1>
      <p class="muted">{t('catalog.subtitle')}</p>
    </div>
  </div>

  <div class="cats">
    {#each categories as cat}
      <Panel>
        <div class="cat-head">
          <strong>{cat.name}</strong>
          <Badge tone="neutral">{catProgress(cat.id)}% {t('catalog.completion')}</Badge>
        </div>
        {#if cat.description}<p class="muted">{cat.description}</p>{/if}
        <div class="cat-foot">
          <span class="count">{t('catalog.skillCount', { count: (cat.skills ?? []).length })}</span>
          <Button variant="ghost" onclick={() => (selected = cat)}>
            {t('catalog.viewSkills')}<Icon name="chevron" size={16} />
          </Button>
        </div>
      </Panel>
    {/each}
  </div>
{/if}

<style>
  .center-spin { display: flex; justify-content: center; padding: 3rem; }
  .head { margin-bottom: 1.2rem; }
  .head.between { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap; }
  .section-title { margin-top: 1.5rem; font-size: 1.3rem; }
  .cats { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; }
  .cat-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 0.6rem; }
  .cat-foot { display: flex; justify-content: space-between; align-items: center; gap: 0.6rem; margin-top: 0.8rem; }
  .count { font-size: 0.85rem; color: var(--muted); }
  .skills { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; }
  .skill-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 0.6rem; }
  .muted { color: var(--muted); }
</style>
