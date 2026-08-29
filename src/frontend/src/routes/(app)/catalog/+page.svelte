<!-- Learner catalog: categories grid → category skills → skill detail with
     recommended/prerequisite strips and a client-side path-generation CTA. -->
<script lang="ts">
  import { apiFetch, ApiError } from '$lib/api/client';
  import { query, invalidate } from '$lib/query';
  import { goto } from '$app/navigation';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Icon from '$lib/icons/Icon.svelte';
  import RecommendedStrip from '$lib/components/RecommendedStrip.svelte';
  import { error as toastError, success } from '$lib/components/ui/toast';
  import { t } from '$lib/i18n';
  import type { SkillDetail } from '$lib/types/api';

  let categories = $state<any[]>([]);
  let progress = $state<any>(null);
  let paths = $state<any[]>([]);
  let growth = $state<any>(null);
  let loading = $state(true);

  let view = $state<'categories' | 'category' | 'skill'>('categories');
  let selectedCategory = $state<any | null>(null);
  let selectedSkillId = $state<number | null>(null);
  let skill = $state<SkillDetail | null>(null);
  let skillLoading = $state(false);
  let generating = $state(false);
  let duplicate = $state(false);

  const norm = (name: string) => (name ?? '').trim().toLowerCase();

  const inPathNames = $derived(
    new Set((paths ?? []).flatMap((p: any) => (p.skills ?? []).map((s: any) => norm(s.name))))
  );
  const masteredNames = $derived(
    new Set((growth?.skills ?? []).filter((g: any) => g.status === 'mastered').map((g: any) => norm(g.skill)))
  );
  const currentMastered = $derived(!!skill && masteredNames.has(norm(skill.name)));
  const currentInPaths = $derived(!!skill && inPathNames.has(norm(skill.name)));

  const catProgress = (id: number) =>
    progress?.categories?.find((p: any) => p.category_id === id)?.completion_percentage ?? 0;

  /** Loads categories + per-category progress + the user's paths and skill
   *  growth independently so a failing sub-call can't blank the page. */
  async function load() {
    loading = true;
    try {
      categories = await query(['catalog', 'categories'], () => apiFetch('/catalog/categories'));
    } catch (e) {
      toastError(String(e instanceof ApiError && e.detail ? e.detail : t('common.error')));
    }
    try {
      progress = await query(['analytics', 'progress-by-category'], () =>
        apiFetch('/analytics/progress-by-category')
      );
    } catch {
      progress = null;
    }
    try {
      paths = await query(['paths'], () => apiFetch('/paths/'));
    } catch {
      paths = [];
    }
    try {
      growth = await query(['skillGrowth'], () => apiFetch('/analytics/skill-growth'));
    } catch {
      growth = null;
    }
    loading = false;
  }

  $effect(() => {
    load();
    const h = () => {
      invalidate(['paths']);
      query(['paths'], () => apiFetch('/paths/')).then((d) => (paths = d)).catch(() => undefined);
    };
    window.addEventListener('sse:path_generated', h);
    return () => window.removeEventListener('sse:path_generated', h);
  });

  /** Opens skill detail (endpoint A); mastery and in-path badges derive after. */
  async function selectSkill(id: number) {
    selectedSkillId = id;
    view = 'skill';
    skillLoading = true;
    skill = null;
    duplicate = false;
    try {
      skill = await query(['catalog', 'skills', String(id)], () => apiFetch('/catalog/skills/' + id));
    } catch (e) {
      toastError(String(e instanceof ApiError && e.detail ? e.detail : t('common.error')));
    } finally {
      skillLoading = false;
    }
  }

  /** Generates a "master this skill" path, invalidates the paths cache and
   *  navigates into the fresh path; 409 reflects the already-in-paths state. */
  async function generate() {
    if (!skill || generating) return;
    generating = true;
    try {
      const path = await apiFetch('/generate-path/skill/' + skill.id, {
        method: 'POST',
        body: { weekly_hours: 10, preferences: null }
      });
      await invalidate(['paths']);
      success(t('wizard.successMessage'));
      goto('/learn/' + path.id);
    } catch (e) {
      if (e instanceof ApiError && e.status === 409) {
        duplicate = true;
        toastError(t('catalog.alreadyInPaths'));
      } else {
        toastError(String(e instanceof ApiError && e.detail ? e.detail : t('common.error')));
      }
    } finally {
      generating = false;
    }
  }

  /** Navigates to the first user path already covering a skill name. */
  function viewPathFor(name: string) {
    const match = (paths ?? []).find((p: any) =>
      (p.skills ?? []).some((s: any) => norm(s.name) === norm(name))
    );
    if (match) goto('/learn/' + match.id);
  }

  /** Strip chip click: open that skill's detail, or its path when covered. */
  function onChipClick(s: any) {
    if (inPathNames.has(norm(s.name))) viewPathFor(s.name);
    else selectSkill(s.id);
  }
</script>

<!-- A · categories overview -->
<div class="head">
  <div>
    <h1>{t('catalog.browse')}</h1>
    <p class="muted">{t('catalog.subtitle')}</p>
  </div>
</div>

{#if view === 'categories'}
  {#if loading}
    <div class="center-spin"><Spinner /></div>
  {:else if categories.length === 0}
    <Panel><p class="muted">{t('catalog.emptyCategories')}</p></Panel>
  {:else}
    <div class="cats">
      {#each categories as cat}
        <Panel>
          <div class="cat-head">
            <strong>{cat.name}</strong>
            {#if progress}
              <Badge tone="accent">{catProgress(cat.id)}% {t('catalog.completion')}</Badge>
            {/if}
          </div>
          {#if cat.description}<p class="muted">{cat.description}</p>{/if}
          <div class="cat-foot">
            <span class="count">{t('catalog.skillCount', { count: (cat.skills ?? []).length })}</span>
            <Button variant="ghost" onclick={() => { selectedCategory = cat; view = 'category'; }}>
              {t('catalog.viewSkills')}<Icon name="chevron" size={16} />
            </Button>
          </div>
        </Panel>
      {/each}
    </div>
  {/if}

{:else if view === 'category'}
  <!-- B · skills in the selected category -->
  <div class="head between">
    <div>
      <h1>{selectedCategory?.name}</h1>
      {#if selectedCategory?.description}<p class="muted">{selectedCategory.description}</p>{/if}
    </div>
    <Button variant="ghost" onclick={() => { view = 'categories'; selectedCategory = null; }}>
      <Icon name="chevron" size={16} />{t('catalog.backToCategories')}
    </Button>
  </div>

  {#if (selectedCategory?.skills ?? []).length === 0}
    <Panel><p class="muted">{t('catalog.emptySkills')}</p></Panel>
  {:else}
    <div class="skills">
      {#each selectedCategory.skills as s}
        <button class="skill-card" onclick={() => selectSkill(s.id)}>
          <div class="skill-head">
            <strong>{s.name}</strong>
            {#if s.difficulty_level}
              <Badge tone="accent">{t('catalog.level')}: {s.difficulty_level}</Badge>
            {/if}
          </div>
          {#if s.description}<p class="muted">{s.description}</p>{/if}
          <small class="muted">
            {s.estimated_hours ?? 0} {t('catalog.hours')}
            {#if s.icon} · {s.icon}{/if}
          </small>
        </button>
      {/each}
    </div>
  {/if}

{:else}
  <!-- C · skill detail -->
  <div class="head between">
    <div>
      <h1>{skill?.name}</h1>
      {#if skill?.category_name}
        <div class="meta-line">
          <Badge tone="neutral">{skill.category_name}</Badge>
          {#if skill?.difficulty_level}
            <Badge tone="accent">{t('catalog.level')}: {skill.difficulty_level}</Badge>
          {/if}
          {#if skill?.estimated_hours}
            <Badge tone="neutral">{skill.estimated_hours} {t('catalog.hours')}</Badge>
          {/if}
        </div>
      {/if}
    </div>
    <Button variant="ghost" onclick={() => { view = 'category'; skill = null; selectedSkillId = null; }}>
      <Icon name="chevron" size={16} />{t('common.back')}
    </Button>
  </div>

  {#if skillLoading}
    <div class="center-spin"><Spinner /></div>
  {:else if skill}
    {#if skill.description}
      <Panel><p class="desc">{skill.description}</p></Panel>
    {/if}

    {#if (skill.recommended ?? []).length}
      <RecommendedStrip
        title={t('catalog.recommendedNext')}
        skills={skill.recommended ?? []}
        inpath={inPathNames}
        onchipclick={onChipClick}
      />
    {/if}

    {#if (skill.prerequisites ?? []).length}
      <RecommendedStrip
        title={t('catalog.prerequisites')}
        skills={skill.prerequisites ?? []}
        inpath={inPathNames}
        onchipclick={onChipClick}
      />
    {/if}

    <div class="cta">
      {#if currentMastered}
        <Badge tone="ok">{t('catalog.mastered')}</Badge>
      {:else if currentInPaths || duplicate}
        <Button disabled>{t('catalog.inYourPaths')}</Button>
        <Button variant="link" onclick={() => viewPathFor(skill?.name ?? '')}>{t('catalog.viewPath')}</Button>
        <span class="muted note">{t('catalog.alreadyInPaths')}</span>
      {:else}
        <Button onclick={generate} loading={generating} disabled={generating}>
          {t('catalog.startLearning')}
        </Button>
      {/if}
    </div>
  {:else}
    <Panel><p class="muted">{t('catalog.skillNotFound')}</p></Panel>
  {/if}
{/if}

<style>
  .center-spin { display: flex; justify-content: center; padding: 3rem; }
  .head { margin-bottom: 1.2rem; }
  .head.between { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap; }
  .meta-line { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.4rem; }
  .cats { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; }
  .cat-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 0.6rem; }
  .cat-foot { display: flex; justify-content: space-between; align-items: center; gap: 0.6rem; margin-top: 0.8rem; }
  .count { font-size: 0.85rem; color: var(--muted); }
  .skills { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; }
  .skill-card {
    text-align: start; background: var(--paper); border: 1px solid var(--line);
    border-radius: var(--radius-lg); padding: 1rem 1.1rem; cursor: pointer;
    display: flex; flex-direction: column; gap: 0.35rem; font-family: var(--font-body);
    color: var(--ink); transition: border-color 0.18s ease, box-shadow 0.18s ease;
  }
  .skill-card:hover { border-color: var(--accent); box-shadow: var(--shadow); }
  .skill-card:focus-visible { outline: none; box-shadow: 0 0 0 3px var(--focus-glow); border-color: var(--accent); }
  .skill-card:active { transform: translateY(1px); }
  .skill-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 0.6rem; }
  .skill-card small { line-height: 1.4; }
  .desc { margin: 0; color: var(--ink-soft); }
  .cta { display: flex; align-items: center; gap: 0.8rem; flex-wrap: wrap; margin-top: 1.4rem; }
  .note { font-size: 0.85rem; }
</style>