<!-- SkillSynth wordmark with a hand-drawn sprout/book mark. Replaces the old logo. -->
<script lang="ts">
  export let compact = false;
</script>

<a class="logo" href="/" aria-label="SkillSynth home">
  <svg width="30" height="30" viewBox="0 0 32 32" fill="none" aria-hidden="true">
    <path d="M16 28C9 28 5 23 5 16c0-5 4-9 11-9s11 4 11 9c0 7-4 12-11 12z" stroke="var(--ochre)" stroke-width="1.8" />
    <path d="M16 27V13M16 18c-3-1-5-3-5-6M16 18c3-1 5-3 5-6" stroke="var(--ochre-deep)" stroke-width="1.8" stroke-linecap="round" />
    <circle cx="16" cy="9" r="2.2" fill="var(--ochre)" />
  </svg>
  {#if !compact}<span class="word">Skill<em>Synth</em></span>{/if}
</a>

<style>
  .logo { display: inline-flex; align-items: center; gap: 0.5rem; color: var(--ink); font-family: var(--font-display); font-weight: 700; font-size: 1.2rem; }
  .logo:hover { text-decoration: none; }
  .word em { font-style: normal; color: var(--ochre-deep); }
</style>
