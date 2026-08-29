<!-- Public landing — editorial Warm Craft rewrite. -->
<script lang="ts">
  import { apiFetch } from '$lib/api/client';
  import { query } from '$lib/query';
  import { t } from '$lib/i18n';
  import Button from '$lib/components/ui/Button.svelte';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Icon from '$lib/icons/Icon.svelte';
  import Illustration from '$lib/components/Illustration.svelte';
  import Logo from '$lib/components/Logo.svelte';
  import LocaleSwitcher from '$lib/components/LocaleSwitcher.svelte';

  const features = [
    { icon: 'path', title: t('landing.featureSmartPaths'), desc: t('landing.featureSmartPathsDesc') },
    { icon: 'analytics', title: 'Track growth', desc: t('landing.featureTrackGrowthDesc') },
    { icon: 'role', title: t('landing.featureRoleSkills'), desc: t('landing.featureRoleSkillsDesc') },
    { icon: 'sparkles', title: t('landing.featureAiAssessment'), desc: t('landing.featureAiAssessmentDesc') },
    { icon: 'check', title: t('landing.featureStepProgress'), desc: t('landing.featureStepProgressDesc') },
    { icon: 'trending', title: t('landing.featureGamified'), desc: t('landing.featureGamifiedDesc') }
  ];
  const how = [
    { n: 1, title: t('landing.howStep1Title'), desc: t('landing.howStep1Desc') },
    { n: 2, title: t('landing.howStep2Title'), desc: t('landing.howStep2Desc') },
    { n: 3, title: t('landing.howStep3Title'), desc: t('landing.howStep3Desc') },
    { n: 4, title: t('landing.howStep4Title'), desc: t('landing.howStep4Desc') }
  ];
  const testimonials = [
    { q: t('landing.testimonial1Quote'), a: t('landing.testimonial1Author'), r: t('landing.testimonial1Role') },
    { q: t('landing.testimonial2Quote'), a: t('landing.testimonial2Author'), r: t('landing.testimonial2Role') },
    { q: t('landing.testimonial3Quote'), a: t('landing.testimonial3Author'), r: t('landing.testimonial3Role') }
  ];

  let stats = $state<any>(null);
  $effect(() => {
    query(['publicStats'], () => apiFetch('/public/stats')).then((d) => (stats = d)).catch(() => {});
  });
  function num(key: string, fallback: number): string {
    const v = stats?.[key];
    return v != null ? String(v) : String(fallback);
  }
</script>

<svelte:head>
  <title>SkillSynth</title>
  <meta name="description" content={t('landing.heroSubtitle')} />
</svelte:head>

<header class="top container between">
  <Logo />
  <nav class="row">
    <LocaleSwitcher />
    <a href="/login">{t('landing.signIn')}</a>
    <Button onclick={() => (location.href = '/register')}>{t('landing.getStarted')}</Button>
  </nav>
</header>

<main>
  <section class="hero container">
    <div class="copy">
      <span class="kicker">{t('landing.badge')}</span>
      <div class="brandmark">
        <h1 class="brandname">Skill<em>Synth</em></h1>
        <Logo compact />
      </div>
      <p class="lede">{t('landing.heroSubtitle')}</p>
      <div class="row">
        <Button onclick={() => (location.href = '/register')}>{t('landing.getStarted')}</Button>
        <Button variant="ghost" onclick={() => (location.href = '/login')}>{t('landing.signIn')}</Button>
      </div>
    </div>
    <div class="art"><Illustration name="hero" width={380} /></div>
  </section>

  <section class="container section">
    <h2 class="center">{t('landing.featuresTitle')}</h2>
    <p class="muted center">{t('landing.featuresSubtitle')}</p>
    <div class="features">
      {#each features as f}
        <Panel>
          <div class="ficon"><Icon name={f.icon} size={22} /></div>
          <h3>{f.title}</h3>
          <p class="muted">{f.desc}</p>
        </Panel>
      {/each}
    </div>
  </section>

  <section class="container section stats-band">
    <div class="stat"><strong>{num('users', 0)}</strong><span>{t('landing.statLearners')}</span></div>
    <div class="stat"><strong>{num('skills', 0)}</strong><span>{t('landing.statSkills')}</span></div>
    <div class="stat"><strong>{num('paths', 0)}</strong><span>{t('landing.statPaths')}</span></div>
    <div class="stat"><strong>{num('resources', 0)}</strong><span>{t('landing.statResources')}</span></div>
  </section>

  <section class="container section">
    <h2 class="center">{t('landing.howTitle')}</h2>
    <p class="muted center">{t('landing.howSubtitle')}</p>
    <div class="how">
      {#each how as h}
        <div class="how-step">
          <span class="num">{h.n}</span>
          <h3>{h.title}</h3>
          <p class="muted">{h.desc}</p>
        </div>
      {/each}
    </div>
  </section>

  <section class="container section">
    <h2 class="center">{t('landing.testimonialsTitle')}</h2>
    <div class="quotes">
      {#each testimonials as tm}
        <blockquote>
          <p>“{tm.q}”</p>
          <footer>— {tm.a}, <span class="muted">{tm.r}</span></footer>
        </blockquote>
      {/each}
    </div>
  </section>

  <section class="container cta">
    <h2>{t('landing.ctaTitle')}</h2>
    <p class="muted">{t('landing.ctaSubtitle')}</p>
    <Button onclick={() => (location.href = '/register')}>{t('landing.ctaButton')}</Button>
  </section>
</main>

<footer class="container foot">
  <Logo />
  <small class="muted">© {new Date().getFullYear()} SkillSynth. {t('landing.footerCopyright')}</small>
</footer>

<style>
  .top { padding-block: 1.2rem; flex-wrap: wrap; gap: 0.75rem; }
  .hero { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 2rem; align-items: center; min-height: 70vh; }
  .kicker { display: inline-block; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: var(--accent-deep); }
  .brandmark { display: flex; flex-direction: column; align-items: flex-start; gap: 0.35rem; margin: 0.3rem 0; }
  .brandname { font-family: var(--font-display); font-size: clamp(2.6rem, 6vw, 4rem); line-height: 1; margin: 0; color: var(--ink); }
  .brandname em { font-style: normal; color: var(--ochre-deep); }
  .hero h1 { font-size: clamp(2.4rem, 5vw, 3.6rem); margin: 0.4rem 0; }
  .lede { font-size: 1.1rem; color: var(--ink-soft); max-width: 42ch; }
  .section { padding-block: 3rem; }
  .center { text-align: center; }
  .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; margin-top: 1.5rem; }
  .features h3 { font-size: 1.05rem; margin: 0.5rem 0 0.3rem; }
  .ficon { color: var(--accent); }
  .stats-band { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; border-block: 1px solid var(--line); padding-block: 2rem; }
  .stat { text-align: center; display: flex; flex-direction: column; gap: 0.2rem; }
  .stat strong { font-family: var(--font-display); font-size: 2rem; color: var(--accent-deep); }
  .stat span { font-size: 0.85rem; color: var(--muted); }
  .how { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.2rem; margin-top: 1.5rem; }
  .num { display: inline-flex; width: 36px; height: 36px; align-items: center; justify-content: center; border-radius: 50%; background: var(--accent); color: #fff; font-weight: 700; }
  .quotes { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1rem; margin-top: 1.5rem; }
  blockquote { margin: 0; background: var(--paper-2); border: 1px solid var(--line); border-inline-start: 3px solid var(--accent); border-radius: var(--radius); padding: 1rem 1.2rem; }
  blockquote footer { margin-top: 0.6rem; font-size: 0.85rem; }
  .cta { text-align: center; background: var(--paper-2); border: 1px solid var(--line); border-radius: var(--radius-lg); padding: 3rem 1.5rem; }
  .cta h2 { font-size: 2rem; }
  .foot { display: flex; align-items: center; gap: 1rem; padding-block: 2rem; border-top: 1px solid var(--line); margin-top: 2rem; }
  @media (max-width: 800px) { .hero { grid-template-columns: 1fr; } .art { order: -1; } .stats-band { grid-template-columns: repeat(2, 1fr); } }
  @media (max-width: 480px) { .stats-band { grid-template-columns: 1fr; } }
</style>
