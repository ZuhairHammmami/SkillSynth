<!-- Hand-drawn SVG illustrations. Strong anti-AI signal — no stock imagery. -->
<script lang="ts">
  export let name: 'hero' | 'empty' | 'sprout' | 'path' = 'sprout';
  export let width = 320;
</script>

{#if name === 'hero'}
  <svg viewBox="0 0 360 240" width={width} fill="none" aria-hidden="true">
    <path d="M20 200 C90 150 130 220 200 170 C260 125 300 180 340 140" stroke="var(--sage-deep)" stroke-width="2" stroke-linecap="round" />
    <path d="M20 210 C90 175 130 230 200 190 C260 158 300 198 340 170" stroke="var(--ochre)" stroke-width="1.4" stroke-dasharray="2 6" stroke-linecap="round" opacity="0.7" />
    <g>
      <path d="M200 170c-10-18-2-34 14-40 6 16-2 34-14 40z" fill="var(--sage)" />
      <path d="M214 130c14-6 28 2 30 16-14 4-28-4-30-16z" fill="var(--ochre)" />
      <circle cx="222" cy="124" r="4" fill="var(--ochre-deep)" />
    </g>
    <g transform="translate(70 150)">
      <rect x="0" y="20" width="46" height="34" rx="3" fill="var(--card)" stroke="var(--ink)" stroke-width="1.6" />
      <path d="M0 20c0-10 46-10 46 0" stroke="var(--ink)" stroke-width="1.6" />
      <path d="M10 32h26M10 40h18" stroke="var(--clay)" stroke-width="1.4" stroke-linecap="round" />
    </g>
    <circle cx="300" cy="60" r="22" fill="var(--ochre)" opacity="0.18" />
    <circle cx="300" cy="60" r="22" stroke="var(--ochre)" stroke-width="1.4" stroke-dasharray="3 5" />
  </svg>
{:else if name === 'empty'}
  <svg viewBox="0 0 200 160" width={width} fill="none" aria-hidden="true">
    <path d="M100 120c-12-22-4-44 20-52 8 20-2 42-20 52z" fill="var(--sage)" />
    <path d="M120 68c16-8 34 4 36 22-18 6-34-6-36-22z" fill="var(--ochre)" />
    <path d="M60 130h90" stroke="var(--line-strong)" stroke-width="2" stroke-linecap="round" />
    <circle cx="100" cy="60" r="3" fill="var(--ochre-deep)" />
  </svg>
{:else if name === 'sprout'}
  <svg viewBox="0 0 120 120" width={width} fill="none" aria-hidden="true">
    <path d="M60 100V54" stroke="var(--sage-deep)" stroke-width="2.4" stroke-linecap="round" />
    <path d="M60 70c-16-4-26-18-24-34 16 2 26 16 24 34z" fill="var(--sage)" />
    <path d="M60 62c14-6 26-2 30 12-16 4-26 0-30-12z" fill="var(--ochre)" />
  </svg>
{:else if name === 'path'}
  <svg viewBox="0 0 200 120" width={width} fill="none" aria-hidden="true">
    <path d="M16 100 C60 80 80 110 120 86 C150 68 170 92 188 70" stroke="var(--ochre)" stroke-width="2.2" stroke-linecap="round" />
    <circle cx="16" cy="100" r="5" fill="var(--sage)" />
    <circle cx="120" cy="86" r="4" fill="var(--ochre-deep)" />
    <circle cx="188" cy="70" r="5" fill="var(--sage-deep)" />
  </svg>
{/if}
