'use client';

import { LandingHeader, LandingFooter, HeroSection, FeaturesSection, StatsSection, HowItWorksSection, TestimonialsSection, CtaSection } from '@/shared/components/LandingSections';

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen">
      <LandingHeader />
      <HeroSection />
      <FeaturesSection />
      <StatsSection />
      <HowItWorksSection />
      <TestimonialsSection />
      <CtaSection />
      <LandingFooter />
    </div>
  );
}
