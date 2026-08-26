<!-- Public landing (placeholder shell; Task 6 expands into full editorial page). -->
<script lang="ts">
  import Illustration from '$lib/components/Illustration.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { t } from '$lib/i18n';
</script>

<header class="top container between">
  <a class="brand" href="/">Skill<em>Synth</em></a>
  <nav class="row">
    <a href="/login">Sign in</a>
    <Button onclick={() => location.href = '/register'}>Get started</Button>
  </nav>
</header>

<main class="hero container">
  <div class="copy">
    <span class="kicker">Adaptive Learning OS</span>
    <h1>Grow skills that<br /><span class="accent">actually stick.</span></h1>
    <p class="lede">{t('landing.subtitle')}</p>
    <div class="row">
      <Button onclick={() => location.href = '/register'}>Start your path</Button>
      <Button variant="ghost" onclick={() => location.href = '/login'}>I already have an account</Button>
    </div>
  </div>
  <div class="art"><Illustration name="hero" width={380} /></div>
</main>

<style>
  .top { padding-block: 1.2rem; }
  .brand { font-family: var(--font-display); font-weight: 700; font-size: 1.3rem; color: var(--ink); }
  .brand em { font-style: normal; color: var(--ochre-deep); }
  .hero { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 2rem; align-items: center; min-height: 72vh; }
  .kicker { display: inline-block; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: var(--ochre-deep); }
  h1 { font-size: clamp(2.4rem, 5vw, 3.6rem); margin: 0.4rem 0; }
  .accent { color: var(--ochre); }
  .lede { font-size: 1.1rem; color: var(--ink-soft); max-width: 38ch; }
  @media (max-width: 800px) { .hero { grid-template-columns: 1fr; } .art { order: -1; } }
</style>
