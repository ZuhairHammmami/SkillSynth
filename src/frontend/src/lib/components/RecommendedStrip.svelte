<!-- Skill strip (Recommended next / Prerequisites): horizontal chips with an
     in-your-paths badge; the parent decides what a chip click does. -->
<script lang="ts">
  import Badge from '$lib/components/ui/Badge.svelte';
  import Icon from '$lib/icons/Icon.svelte';
  import { t } from '$lib/i18n';

  let {
    title,
    skills = [],
    inpath = new Set<string>(),
    onchipclick
  }: {
    title: string;
    skills: any[];
    inpath: Set<string>;
    onchipclick: (s: any) => void;
  } = $props();

  const norm = (name: string) => (name ?? '').trim().toLowerCase();
  const covered = (s: any) => inpath.has(norm(s.name));
</script>

<section class="strip">
  <h2 class="strip-title">{title}</h2>
  <div class="chips">
    {#each skills as s}
      <button class="chip" onclick={() => onchipclick(s)}>
        <strong>{s.name}</strong>
        <span class="chip-meta">
          {#if s.difficulty_level}
            <Badge tone="neutral">{t('catalog.level')}: {s.difficulty_level}</Badge>
          {/if}
          {#if covered(s)}
            <Badge tone="ok"><Icon name="check" size={12} />{t('catalog.inYourPaths')}</Badge>
          {/if}
        </span>
      </button>
    {/each}
  </div>
</section>

<style>
  .strip { margin-top: 1.6rem; }
  .strip-title { font-size: 1.3rem; margin-bottom: 0.6rem; }
  .chips { display: flex; gap: 0.6rem; overflow-x: auto; padding-block: 0.15rem; }
  .chip {
    flex-shrink: 0; display: inline-flex; flex-direction: column; align-items: flex-start;
    gap: 0.3rem; text-align: start; background: var(--paper);
    border: 1px solid var(--line); border-radius: var(--radius);
    padding: 0.6rem 0.8rem; cursor: pointer; font-family: var(--font-body); color: var(--ink);
    min-width: 150px; transition: border-color 0.18s ease, background 0.18s ease;
  }
  .chip:hover { border-color: var(--accent); background: var(--accent-soft); }
  .chip:focus-visible { outline: none; box-shadow: 0 0 0 3px var(--focus-glow); border-color: var(--accent); }
  .chip-meta { display: flex; flex-wrap: wrap; gap: 0.3rem; align-items: center; }
</style>