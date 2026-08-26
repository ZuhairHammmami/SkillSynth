<!-- Top skills list with proficiency + status badge. -->
<script lang="ts">
  import type { SkillGrowthItem } from '$lib/types/api';
  import Badge from '$lib/components/ui/Badge.svelte';
  import ProgressMeter from './ProgressMeter.svelte';

  let { items = [] }: { items?: SkillGrowthItem[] } = $props();
  function tone(s: string): string {
    if (s === 'mastered') return 'ok';
    if (s === 'learning') return 'sage';
    return 'neutral';
  }
</script>

<ul class="list">
  {#each items as it}
    <li>
      <div class="row">
        <span class="name">{it.skill}</span>
        <Badge tone={tone(it.status)}>{it.status}</Badge>
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
