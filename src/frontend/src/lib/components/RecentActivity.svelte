<!-- Recent-activity feed. Renders caller-supplied items (title ?? message) with
     a small dot per row and a bilingual relative timestamp computed from
     created_at via Intl.RelativeTimeFormat / toLocaleDateString (ar vs en).
     The empty-state text is passed in by the caller as `empty` via t() —
     this component formats dates but never prints hardcoded visible strings. -->
<script lang="ts">
  import { i18n } from '$lib/i18n';
  import Icon from '$lib/icons/Icon.svelte';

  type Item = { id?: string | number; title?: string; message?: string; created_at?: string };

  let {
    items = [],
    max = 6,
    empty
  }: { items?: Item[]; max?: number; empty?: string } = $props();

  const visible = $derived(items.slice(0, max));
  /** Range-forcing Intl formatter; recreated per call so it always follows the
   *  current locale instead of caching the locale at component init. */
  function formatter(delta: number, unit: Intl.RelativeTimeFormatUnit): string {
    return new Intl.RelativeTimeFormat(i18n.locale === 'ar' ? 'ar' : 'en', {
      numeric: 'auto'
    }).format(delta, unit);
  }

  function relativeTime(iso?: string): string {
    // Returns a compact "3 hours ago" (bilingual) or absolute short date.
    if (!iso) return '';
    const then = new Date(iso).getTime();
    if (Number.isNaN(then)) return '';
    const secs = Math.round((then - Date.now()) / 1000);
    const abs = Math.abs(secs);
    if (abs < 60) return formatter(0, 'second');
    if (abs < 3600) return formatter(Math.round(secs / 60), 'minute');
    if (abs < 86400) return formatter(Math.round(secs / 3600), 'hour');
    if (abs < 604800) return formatter(Math.round(secs / 86400), 'day');
    return new Date(iso).toLocaleDateString(i18n.locale === 'ar' ? 'ar-EG' : 'en-US', {
      year: 'numeric', month: 'short', day: 'numeric'
    });
  }
</script>

{#if visible.length === 0}
  <p class="muted empty">{empty}</p>
{:else}
  <ul class="feed">
    {#each visible as it (it.id ?? it.title ?? it.message)}
      <li>
        <span class="dot"><Icon name="check" size={12} /></span>
        <div class="body">
          <div class="text">{it.title ?? it.message ?? ''}</div>
          {#if it.created_at}
            <div class="time">{relativeTime(it.created_at)}</div>
          {/if}
        </div>
      </li>
    {/each}
  </ul>
{/if}

<style>
  .empty { padding: 1.2rem 0; }
  .feed { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; }
  .feed li { display: flex; align-items: flex-start; gap: 0.6rem; padding: 0.6rem 0; border-block-end: 1px solid var(--line); }
  .feed li:first-child { padding-block-start: 0; }
  .feed li:last-child { border-block-end: 0; padding-block-end: 0; }
  .dot { width: 20px; height: 20px; flex-shrink: 0; border-radius: 50%; background: var(--accent-soft);
    color: var(--accent-deep); display: inline-flex; align-items: center; justify-content: center; margin-block-start: 0.1rem; }
  .body { display: flex; flex-direction: column; gap: 0.15rem; min-width: 0; }
  .text { font-size: 0.9rem; color: var(--ink); }
  .time { font-size: 0.72rem; color: var(--muted); }
</style>
