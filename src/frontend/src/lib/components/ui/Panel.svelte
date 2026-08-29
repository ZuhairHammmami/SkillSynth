<!-- Panel: the Warm-Craft replacement for the SaaS "card". Hairline border,
     paper surface, optional title/footer slots. No drop shadows. -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  let { title, subtitle, children, footer }: any = $props();
</script>

<section class="panel">
  {#if title || subtitle}
    <header class="panel-head">
      {#if title}<h3>{title}</h3>{/if}
      {#if subtitle}<p class="muted">{subtitle}</p>{/if}
    </header>
  {/if}
  <div class="panel-body">{@render children()}</div>
  {#if footer}<footer class="panel-foot">{@render footer()}</footer>{/if}
</section>

<style>
  .panel {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: var(--radius-lg);
    padding: 1.25rem;
    box-shadow: var(--shadow);
  }
  .panel-head { margin-bottom: 0.9rem; }
  .panel-head h3 { font-size: 1.15rem; margin: 0; }
  .panel-head p { margin: 0.2rem 0 0; font-size: 0.85rem; }
  .panel-foot { margin-top: 1rem; padding-top: 0.9rem; border-top: 1px solid var(--line); }
</style>
