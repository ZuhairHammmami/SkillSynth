'use client';

import { useTranslations } from 'next-intl';
import { ArrowLeft, ArrowRight } from 'lucide-react';
import { Button } from '@/shared/ui/button';
import type { Step } from './types';

interface StepNavigationProps {
  step: Step;
  totalSteps: number;
  canProceed: boolean;
  onBack: () => void;
  onNext: () => void;
}

export function StepNavigation({ step, totalSteps, canProceed, onBack, onNext }: StepNavigationProps) {
  const t = useTranslations('wizard');

  return (
    <div className="flex items-center justify-between pt-2 border-t">
      <div>
        {step > 1 && (
          <Button variant="ghost" onClick={onBack}>
            <ArrowLeft className="me-2 h-4 w-4" />
            {t('back')}
          </Button>
        )}
      </div>
      <div>
        {step < totalSteps && (
          <Button onClick={onNext} disabled={!canProceed}>
            {t('next')}
            <ArrowRight className="ms-2 h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  );
}
