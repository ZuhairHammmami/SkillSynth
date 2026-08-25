'use client';

import { useTranslations } from 'next-intl';
import { PathWizard } from '@/shared/components/PathWizard';

export default function WizardPage() {
  const t = useTranslations('wizard');

  return (
    <div className="flex min-h-screen items-center justify-center p-8">
      <div className="mx-auto max-w-lg text-center space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{t('generatePath')}</h1>
          <p className="text-sm text-muted-foreground mt-2">
            {t('pageSubtitle') || 'Answer a few questions to generate a personalized learning path'}
          </p>
        </div>
        <PathWizard />
      </div>
    </div>
  );
}
