'use client';

import { useTranslations } from 'next-intl';
import { Sparkles, Loader2 } from 'lucide-react';
import { Card, CardContent } from '@/shared/ui/card';
import { Button } from '@/shared/ui/button';
import { RadioGroup, RadioGroupItem } from '@/shared/ui/radio-group';
import { Label } from '@/shared/ui/label';
import type { WizardQuestion } from '@/shared/hooks/useAssessmentApi';

interface AssessmentStepProps {
  hasSkillProfile: boolean;
  questions: WizardQuestion[];
  isLoading: boolean;
  answers: Record<string, number>;
  onAnswer: (questionId: string, optionIndex: number) => void;
  onSkip: () => void;
  onStart: () => void;
}

export function AssessmentStep({
  hasSkillProfile, questions, isLoading, answers, onAnswer, onSkip, onStart,
}: AssessmentStepProps) {
  const t = useTranslations('wizard');

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-10">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
        <p className="text-sm text-muted-foreground">{t('assessmentLoading')}</p>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div className="space-y-4 py-4">
        <Card className="border-primary/20 bg-primary/5">
          <CardContent className="p-6 text-center space-y-3">
            <div className="inline-flex items-center justify-center h-12 w-12 rounded-full bg-primary/10 mx-auto">
              <Sparkles className="h-6 w-6 text-primary" />
            </div>
            <p className="text-sm font-medium">{t('assessmentNone')}</p>
          </CardContent>
        </Card>
        <div className="flex flex-col items-center gap-3">
          <Button className="w-full sm:w-auto" onClick={onStart}>
            <Sparkles className="me-2 h-4 w-4" />
            {t('continueWithoutAssessment')}
          </Button>
        </div>
      </div>
    );
  }

  const skills = [...new Set(questions.map((q) => q.skill))];
  const answeredCount = Object.keys(answers).length;

  return (
    <div className="space-y-4 py-4">
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <p>{t('assessmentPrompt')}</p>
        <span>
          {t('assessmentProgress', { answered: answeredCount, total: questions.length })}
        </span>
      </div>
      {skills.map((skill) => (
        <Card key={skill} className="border-border/60">
          <CardContent className="p-4 space-y-3">
            <h4 className="text-sm font-semibold">{skill}</h4>
            {questions.filter((q) => q.skill === skill).map((q, qi) => (
              <div key={q.id} className="space-y-2">
                <p className="text-sm">
                  {t('questionLabel', { n: qi + 1 })} — {q.text}
                </p>
                <RadioGroup
                  value={answers[q.id] !== undefined ? String(answers[q.id]) : undefined}
                  onValueChange={(v) => onAnswer(q.id, Number(v))}
                  className="ps-2"
                >
                  {q.options.map((option, oi) => (
                    <div key={oi} className="flex items-center gap-2">
                      <RadioGroupItem value={String(oi)} id={`${q.id}-${oi}`} />
                      <Label htmlFor={`${q.id}-${oi}`} className="text-sm font-normal">
                        {option}
                      </Label>
                    </div>
                  ))}
                </RadioGroup>
              </div>
            ))}
          </CardContent>
        </Card>
      ))}
      <div className="flex flex-col items-center gap-3">
        <Button className="w-full sm:w-auto" onClick={onStart}>
          <Sparkles className="me-2 h-4 w-4" />
          {t('continueWithAssessment')}
        </Button>
        {hasSkillProfile && (
          <button
            type="button"
            onClick={onSkip}
            className="text-xs text-muted-foreground underline underline-offset-2 hover:text-foreground transition-colors"
          >
            {t('skipAssessmentLink')}
          </button>
        )}
      </div>
    </div>
  );
}