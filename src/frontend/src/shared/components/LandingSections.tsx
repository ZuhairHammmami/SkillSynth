'use client';

import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { Logo } from '@/shared/components/Logo';
import { LocaleSwitcher } from '@/shared/components/LocaleSwitcher';
import { Button } from '@/shared/ui/button';
import { ArrowRight, BookOpen, BarChart3, Users, Sparkles, CheckCircle, Star, Route, Library } from 'lucide-react';
import { useEffect, useState } from 'react';

const features = [
  { icon: BookOpen, titleKey: 'featureSmartPaths', descKey: 'featureSmartPathsDesc' },
  { icon: BarChart3, titleKey: 'featureTrackGrowth', descKey: 'featureTrackGrowthDesc' },
  { icon: Users, titleKey: 'featureRoleSkills', descKey: 'featureRoleSkillsDesc' },
  { icon: Sparkles, titleKey: 'featureAiAssessment', descKey: 'featureAiAssessmentDesc' },
  { icon: CheckCircle, titleKey: 'featureStepProgress', descKey: 'featureStepProgressDesc' },
  { icon: Star, titleKey: 'featureGamified', descKey: 'featureGamifiedDesc' },
];

interface PublicStats {
  users: number;
  skills: number;
  paths: number;
  resources: number;
}

function formatStat(n: number): string {
  if (n >= 1000) return `${Math.floor(n / 1000)}K+`;
  return `${n}+`;
}

function StatsSectionInner() {
  const t = useTranslations('landing');
  const [stats, setStats] = useState<{ labelKey: string; value: string }[] | null>(null);

  useEffect(() => {
    const base = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';
    fetch(`${base}/public/stats`)
      .then(r => r.json())
      .then((data: PublicStats) => {
        setStats([
          { labelKey: 'statLearners', value: formatStat(data.users) },
          { labelKey: 'statSkills', value: formatStat(data.skills) },
          { labelKey: 'statPaths', value: formatStat(data.paths) },
          { labelKey: 'statResources', value: formatStat(data.resources) },
        ]);
      })
      .catch(() => {
        setStats([
          { labelKey: 'statLearners', value: '—' },
          { labelKey: 'statSkills', value: '—' },
          { labelKey: 'statPaths', value: '—' },
          { labelKey: 'statResources', value: '—' },
        ]);
      });
  }, []);

  return (
    <section className="border-t py-16 md:py-24 bg-muted/50">
      <div className="container">
        <div className="mx-auto max-w-2xl text-center mb-12">
          <h2 className="text-3xl font-bold tracking-tight">{t('statsTitle')}</h2>
          <p className="mt-4 text-muted-foreground">{t('statsSubtitle')}</p>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {(stats ?? []).map((s) => (
            <div key={s.labelKey} className="text-center">
              <div className="text-3xl font-bold">{s.value}</div>
              <div className="text-sm text-muted-foreground mt-1">{t(s.labelKey)}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

const howItWorks = [
  { step: '01', titleKey: 'howStep1Title', descKey: 'howStep1Desc' },
  { step: '02', titleKey: 'howStep2Title', descKey: 'howStep2Desc' },
  { step: '03', titleKey: 'howStep3Title', descKey: 'howStep3Desc' },
  { step: '04', titleKey: 'howStep4Title', descKey: 'howStep4Desc' },
];

const testimonials = [
  { quoteKey: 'testimonial1Quote', authorKey: 'testimonial1Author', roleKey: 'testimonial1Role' },
  { quoteKey: 'testimonial2Quote', authorKey: 'testimonial2Author', roleKey: 'testimonial2Role' },
  { quoteKey: 'testimonial3Quote', authorKey: 'testimonial3Author', roleKey: 'testimonial3Role' },
];

export function LandingHeader() {
  const t = useTranslations('landing');
  return (
    <header className="sticky top-0 z-50 border-b bg-background/95">
      <div className="container flex h-14 items-center justify-between">
        <Logo />
        <div className="flex items-center gap-4">
          <LocaleSwitcher />
          <Button variant="ghost" size="sm" asChild><Link href="/login">{t('signIn')}</Link></Button>
          <Button size="sm" asChild><Link href="/register">{t('getStarted')}</Link></Button>
        </div>
      </div>
    </header>
  );
}

export function LandingFooter() {
  const t = useTranslations('landing');
  return (
    <footer className="border-t py-8">
      <div className="container flex flex-col sm:flex-row items-center justify-between gap-4">
        <Logo />
        <p className="text-sm text-muted-foreground">{t('footerCopyright')}</p>
      </div>
    </footer>
  );
}

export function HeroSection() {
  const t = useTranslations('landing');
  return (
    <section className="container pt-24 pb-16 md:pt-32 md:pb-24">
      <div className="mx-auto max-w-3xl text-center">
        <div className="mb-6 inline-flex items-center gap-2 rounded-full border bg-muted px-4 py-1.5 text-sm text-muted-foreground">
          <Sparkles className="h-3.5 w-3.5" />{t('badge')}
        </div>
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl text-balance">{t('heroTitle')}</h1>
        <p className="mt-6 text-lg text-muted-foreground max-w-2xl mx-auto text-pretty">{t('heroSubtitle')}</p>
        <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Button size="xl" asChild><Link href="/register">{t('ctaStart')}<ArrowRight className="ms-2 h-5 w-5" /></Link></Button>
          <Button variant="outline" size="xl" asChild><Link href="#features">{t('ctaHowItWorks')}</Link></Button>
        </div>
      </div>
    </section>
  );
}

export function FeaturesSection() {
  const t = useTranslations('landing');
  return (
    <section id="features" className="border-t py-16 md:py-24">
      <div className="container">
        <div className="mx-auto max-w-2xl text-center mb-12">
          <h2 className="text-3xl font-bold tracking-tight">{t('featuresTitle')}</h2>
          <p className="mt-4 text-muted-foreground">{t('featuresSubtitle')}</p>
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {features.map((f) => (
            <div key={f.titleKey} className="rounded-lg border p-6 hover:shadow-sm transition-shadow">
              <f.icon className="h-8 w-8 text-primary mb-4" />
              <h3 className="font-semibold mb-2">{t(f.titleKey)}</h3>
              <p className="text-sm text-muted-foreground">{t(f.descKey)}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export const StatsSection = StatsSectionInner;

export function HowItWorksSection() {
  const t = useTranslations('landing');
  return (
    <section className="border-t py-16 md:py-24">
      <div className="container">
        <div className="mx-auto max-w-2xl text-center mb-12">
          <h2 className="text-3xl font-bold tracking-tight">{t('howTitle')}</h2>
          <p className="mt-4 text-muted-foreground">{t('howSubtitle')}</p>
        </div>
        <div className="grid gap-8 md:grid-cols-4">
          {howItWorks.map((item) => (
            <div key={item.step} className="text-center">
              <div className="inline-flex items-center justify-center h-12 w-12 rounded-full bg-primary/10 text-primary font-bold text-lg mb-4">{item.step}</div>
              <h3 className="font-semibold mb-2">{t(item.titleKey)}</h3>
              <p className="text-sm text-muted-foreground">{t(item.descKey)}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export function TestimonialsSection() {
  const t = useTranslations('landing');
  return (
    <section className="border-t py-16 md:py-24 bg-muted/50">
      <div className="container">
        <div className="mx-auto max-w-2xl text-center mb-12">
          <h2 className="text-3xl font-bold tracking-tight">{t('testimonialsTitle')}</h2>
        </div>
        <div className="grid gap-6 md:grid-cols-3">
          {testimonials.map((tItem) => (
            <div key={tItem.authorKey} className="rounded-lg border bg-card p-6">
              <p className="text-sm leading-relaxed mb-4">&ldquo;{t(tItem.quoteKey)}&rdquo;</p>
              <div>
                <p className="text-sm font-semibold">{t(tItem.authorKey)}</p>
                <p className="text-xs text-muted-foreground">{t(tItem.roleKey)}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export function CtaSection() {
  const t = useTranslations('landing');
  return (
    <section className="border-t py-16 md:py-24">
      <div className="container">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight">{t('ctaTitle')}</h2>
          <p className="mt-4 text-muted-foreground">{t('ctaSubtitle')}</p>
          <div className="mt-8">
            <Button size="xl" asChild><Link href="/register">{t('ctaButton')}<ArrowRight className="ms-2 h-5 w-5" /></Link></Button>
          </div>
        </div>
      </div>
    </section>
  );
}
