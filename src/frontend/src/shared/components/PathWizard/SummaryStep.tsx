'use client';

import { useTranslations } from 'next-intl';
import { Sparkles, Zap } from 'lucide-react';
import { Card, CardContent } from '@/shared/ui/card';
import { Badge } from '@/shared/ui/badge';
import { Button } from '@/shared/ui/button';
import type { WizardState } from './types';

interface SummaryStepProps {
  state: WizardState;
  isPending: boolean;
  isError: boolean;
  onGenerate: () => void;
}

function capitalize(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

export function SummaryStep({ state, isPending, isError, onGenerate }: SummaryStepProps) {
  const t = useTranslations('wizard');

  return (
    <div className="space-y-4">
      <Card>
        <CardContent className="p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">{t('summaryGoal')}</span>
            <Badge variant="secondary">{state.selectedRole?.title}</Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">{t('summaryLevel')}</span>
            <span className="text-sm font-medium">{t(`level${capitalize(state.skillLevel)}`)}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">{t('summaryHours')}</span>
            <span className="text-sm font-medium">{state.weeklyHours}h/week</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">{t('summaryFormat')}</span>
            <span className="text-sm font-medium">{t(`format${capitalize(state.format)}`)}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">{t('summaryLanguage')}</span>
            <span className="text-sm font-medium">{t(`language${state.language.toUpperCase()}`)}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">{t('summaryFreeContent')}</span>
            <span className="text-sm font-medium">{state.freeContentOnly ? t('summaryYes') : t('summaryNo')}</span>
          </div>
          {state.assessmentQueued && (
            <div className="flex items-center gap-2 rounded-md border border-amber-200 bg-amber-50 p-2 text-xs text-amber-800">
              <Sparkles className="h-3.5 w-3.5 shrink-0" />
              {t('assessmentQueued')}
            </div>
          )}
        </CardContent>
      </Card>

      <Button
        className="w-full"
        size="xl"
        onClick={onGenerate}
        disabled={isPending}
      >
        {isPending ? (
          <>
            <Zap className="me-2 h-4 w-4 animate-pulse" />
            {t('generating')}
          </>
        ) : (
          <>
            <Sparkles className="me-2 h-4 w-4" />
            {t('generateButton')}
          </>
        )}
      </Button>

      {isError && (
        <p className="text-sm text-destructive text-center">{t('errorMessage')}</p>
      )}
    </div>
  );
}
