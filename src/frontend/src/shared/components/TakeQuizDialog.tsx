'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { Loader2, Sparkles } from 'lucide-react';
import { toast } from 'sonner';
import apiClient from '@/shared/lib/api';
import { sseBus } from '@/shared/lib/sseBus';
import { Badge } from '@/shared/ui/badge';
import { Button } from '@/shared/ui/button';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription,
} from '@/shared/ui/dialog';
import { Label } from '@/shared/ui/label';
import { RadioGroup, RadioGroupItem } from '@/shared/ui/radio-group';
import type { WizardQuestion } from '@/shared/hooks/useAssessmentApi';
import type { ExplainPayload } from '@/types/api';

interface TakeQuizDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  skillId: number;
  skillName: string;
  assessmentId: number | null;
}

/** Submit payload of POST /assessments/submit (score is a percentage;
 * per-question correctness comes back in responses). */
interface QuizSubmitResult {
  score: number;
  total_questions: number;
  responses: {
    question_index: number;
    is_correct: boolean;
    correct_answer: string | null;
  }[];
}

/** Practice-quiz dialog (SS-AI): renders the questions of one skill's
 * assessment, grades them through POST /assessments/submit and offers
 * POST /ai/explain walkthrough. Opened by the analytics weaknesses panel
 * once SSE ai_test_ready delivers the generated assessment_id. */
export function TakeQuizDialog({
  open, onOpenChange, skillId, skillName, assessmentId,
}: TakeQuizDialogProps) {
  const t = useTranslations('ai');
  const tw = useTranslations('wizard');
  const [questions, setQuestions] = useState<WizardQuestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<QuizSubmitResult | null>(null);
  const [explaining, setExplaining] = useState(false);
  const [explain, setExplain] = useState<ExplainPayload | null>(null);
  const [delta, setDelta] = useState<number | null>(null);

  useEffect(() => {
    if (open) return;
    setQuestions([]);
    setIsLoading(false);
    setAnswers({});
    setSubmitting(false);
    setResult(null);
    setExplaining(false);
    setExplain(null);
    setDelta(null);
  }, [open]);

  // Fetch this skill's frozen question payload on every open.
  useEffect(() => {
    if (!open || !skillId) return;
    let cancelled = false;
    setIsLoading(true);
    apiClient
      .get<WizardQuestion[]>(`/assessments/${skillId}/questions`)
      .then((res) => {
        if (!cancelled) setQuestions(res.data.filter((q) => q.skill === skillName));
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [open, skillId, skillName]);

  // Surface async AI proficiency reviews for this skill while open.
  useEffect(() => {
    if (!open) return;
    const off = sseBus.on('proficiency_adjusted', (frame) => {
      const data = frame as unknown as { skill_id: number; delta: number };
      if (data.skill_id !== skillId) return;
      setDelta(data.delta);
    });
    return off;
  }, [open, skillId]);

  const orderedAnswers = () =>
    questions.map((q) => (answers[q.id] !== undefined ? answers[q.id] : -1));

  const allAnswered =
    questions.length > 0 && questions.every((q) => answers[q.id] !== undefined);

  const handleSubmit = async () => {
    if (!assessmentId || submitting) return;
    setSubmitting(true);
    try {
      const res = await apiClient.post<QuizSubmitResult>('/assessments/submit', {
        assessment_id: assessmentId,
        answers: orderedAnswers(),
      });
      setResult(res.data);
    } catch {
      toast.error(t('submitFailed'));
    } finally {
      setSubmitting(false);
    }
  };

  const handleExplain = async () => {
    if (!assessmentId || explaining) return;
    setExplaining(true);
    try {
      const res = await apiClient.post<ExplainPayload>('/ai/explain', {
        assessment_id: assessmentId,
        answers: orderedAnswers(),
      });
      setExplain(res.data);
    } catch {
      toast.error(t('aiDisabled'));
    } finally {
      setExplaining(false);
    }
  };

  const correctCount = result
    ? result.responses.filter((r) => r.is_correct).length
    : 0;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{skillName}</DialogTitle>
          <DialogDescription>{t('takeQuiz')}</DialogDescription>
        </DialogHeader>

        {isLoading && (
          <div className="flex flex-col items-center gap-3 py-8">
            <Loader2 className="h-6 w-6 animate-spin text-primary" />
            <p className="text-sm text-muted-foreground">{t('loadingQuestions')}</p>
          </div>
        )}

        {!isLoading && questions.length === 0 && !result && (
          <p className="text-sm text-muted-foreground py-6 text-center">
            {t('noQuestions')}
          </p>
        )}

        {!isLoading && !result && questions.length > 0 && (
          <div className="space-y-4 py-2">
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>
                {tw('assessmentProgress', {
                  answered: Object.keys(answers).length,
                  total: questions.length,
                })}
              </span>
            </div>
            {questions.map((q, qi) => (
              <div key={q.id} className="rounded-lg border bg-card p-3 space-y-2">
                <p className="text-sm">
                  {tw('questionLabel', { n: qi + 1 })} — {q.text}
                </p>
                <RadioGroup
                  value={answers[q.id] !== undefined ? String(answers[q.id]) : undefined}
                  onValueChange={(v) => setAnswers((prev) => ({ ...prev, [q.id]: Number(v) }))}
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
            <Button
              className="w-full"
              onClick={handleSubmit}
              disabled={!allAnswered || submitting}
            >
              {submitting && <Loader2 className="me-2 h-4 w-4 animate-spin" />}
              {t('submitQuiz')}
            </Button>
          </div>
        )}

        {result && (
          <div className="space-y-4 py-2">
            <div className="rounded-lg border bg-card p-4 space-y-2 text-center">
              <p className="text-2xl font-bold">
                {t('scoreLabel', { correct: correctCount, total: result.total_questions })}
              </p>
              {delta !== null && (
                <Badge variant="secondary">{t('levelAdjusted', { delta })}</Badge>
              )}
            </div>

            {!explain && (
              <Button
                variant="outline"
                className="w-full"
                onClick={handleExplain}
                disabled={explaining}
              >
                {explaining ? (
                  <Loader2 className="me-2 h-4 w-4 animate-spin" />
                ) : (
                  <Sparkles className="me-2 h-4 w-4" />
                )}
                {t('explainResults')}
              </Button>
            )}

            {explain && (
              <div className="space-y-3">
                <h4 className="text-sm font-semibold">{t('explanationsTitle')}</h4>
                {explain.explanations.map((e) => (
                  <div key={e.question_index} className="rounded-lg border bg-card p-3 space-y-1">
                    <p className="text-sm font-medium">
                      {questions[e.question_index]?.text ??
                        tw('questionLabel', { n: e.question_index + 1 })}
                    </p>
                    <p className="text-xs text-muted-foreground leading-relaxed">{e.why}</p>
                  </div>
                ))}
                {explain.advice && (
                  <div className="rounded-lg border border-primary/20 bg-primary/5 p-3 space-y-1">
                    <h4 className="text-sm font-semibold">{t('adviceTitle')}</h4>
                    <p className="text-xs text-muted-foreground leading-relaxed">
                      {explain.advice}
                    </p>
                  </div>
                )}
              </div>
            )}

            <Button variant="ghost" className="w-full" onClick={() => onOpenChange(false)}>
              {t('close')}
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
