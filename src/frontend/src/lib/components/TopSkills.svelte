<!-- Top skills list with proficiency + status badge. -->
<script lang="ts">
  import type { SkillGrowthItem } from '$lib/types/api';
  import Badge from '$lib/components/ui/Badge.svelte';
  import ProgressMeter from './ProgressMeter.svelte';
  import { t } from '$lib/i18n';

  let { items = [] }: { items?: SkillGrowthItem[] } = $props();
  function tone(s: string): string {
    if (s === 'mastered') return 'ok';
    if (s === 'learning') return 'accent';
    return 'neutral';
  }
  const statusLabel = $derived<Record<string, string>>({
    mastered: t('units.mastered'),
    learning: t('units.learning'),
    not_started: t('skills.notStarted'),
    completed: t('units.completed')
  });
</script>

<ul class="list">
  {#each items as it}
    <li>
      <div class="row">
        <span class="name">{it.skill}</span>
        <Badge tone={tone(it.status)}>{statusLabel[it.status] ?? it.status}</Badge>
      </div>
      <ProgressMeter value={it.proficiency * 20} />
    </li>
  {/each}
</ul>

<style>
  .list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.9rem; }
  .row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem; }
  .name { font-weight: 600; }
</style>
