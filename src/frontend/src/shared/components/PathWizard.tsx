'use client';

import { useState, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { toast } from 'sonner';
import { Plus } from 'lucide-react';
import { Button } from '@/shared/ui/button';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
  DialogDescription, DialogTrigger,
} from '@/shared/ui/dialog';
import { useGeneratePath } from '@/shared/hooks/usePathApi';
import { useWizardOptions } from '@/shared/hooks/useSystemApi';
import { useProfile } from '@/shared/hooks/useAuthApi';
import { useRoleQuestions, type WizardQuestion } from '@/shared/hooks/useAssessmentApi';
import { useGenerateWizardQuiz, useWizardAnalysis } from '@/shared/hooks/useAiApi';
import { sseBus } from '@/shared/lib/sseBus';
import { GoalStep } from '@/shared/components/PathWizard/GoalStep';
import { PreferencesStep } from '@/shared/components/PathWizard/PreferencesStep';
import { AssessmentStep } from '@/shared/components/PathWizard/AssessmentStep';
import { ResultsStep } from '@/shared/components/PathWizard/ResultsStep';
import { SummaryStep } from '@/shared/components/PathWizard/SummaryStep';
import { StepNavigation } from '@/shared/components/PathWizard/StepNavigation';
import type { WizardState, Step } from '@/shared/components/PathWizard/types';
import { INITIAL_STATE } from '@/shared/components/PathWizard/types';

const STEP_COUNT = 5;

/** Learning-path wizard dialog (SS-AI two-phase): steps 1-3 collect
 * goal/preferences/answers (optionally replacing role questions with an
 * AI-generated quiz), step 4 shows the POST /wizard/analysis diagnostic
 * report, step 5 summarizes before useGeneratePath creates the path.
 * Consumes sseBus frames emitted by useSSE; rendered from dashboard/paths pages. */
export function PathWizard() {
  const router = useRouter();
  const t = useTranslations('wizard');
  const tAi = useTranslations('ai');
  const [open, setOpen] = useState(false);
  const [state, setState] = useState<WizardState>(INITIAL_STATE);
  const [aiQuestions, setAiQuestions] = useState<WizardQuestion[]>([]);
  const { data: options, isLoading: optionsLoading } = useWizardOptions();
  const { data: profile } = useProfile();
  const generatePath = useGeneratePath();
  const generateQuiz = useGenerateWizardQuiz();
  const analysis = useWizardAnalysis();

  const roles = options?.job_roles as { title: string; career_field: string }[] | undefined;
  const hasSkillProfile = profile?.skill_profile != null;
  const { data: roleQuestions = [], isLoading: questionsLoading } = useRoleQuestions(
    state.selectedRole?.title ?? null
  );
  const questions = aiQuestions.length > 0 ? aiQuestions : roleQuestions;

  const set = useCallback(<K extends keyof WizardState>(key: K, value: WizardState[K]) => {
    setState((prev) => ({ ...prev, [key]: value }));
  }, []);

  const goTo = useCallback((step: Step) => set('step', step), [set]);

  const canProceed = state.step === 1 ? !!state.selectedRole : true;

  const handleOpen = useCallback((o: boolean) => {
    setOpen(o);
    if (!o) {
      setState(INITIAL_STATE);
      setAiQuestions([]);
    }
  }, []);

  const handleGenerateQuiz = useCallback(async () => {
    if (!state.selectedRole) return;
    try {
      const { job_id } = await generateQuiz.mutateAsync(state.selectedRole.title);
      set('quizJobId', job_id);
    } catch {
      toast.error(tAi('quizFailed'));
    }
  }, [state.selectedRole, generateQuiz, set, tAi]);

  const handleAssessmentContinue = useCallback((queued: boolean) => {
    set('assessmentQueued', queued);
    goTo(4);
    if (!state.selectedRole) return;
    analysis
      .mutateAsync({
        goal: state.selectedRole.title,
        weekly_hours: state.weeklyHours,
        answers: state.answers,
      })
      .then((report) => set('analysis', report))
      .catch(() => toast.error(tAi('analysisFailed')));
  }, [state, set, goTo, analysis, tAi]);

  // SS-AI quiz delivery: the POST /ai/wizard-quiz job resolves over SSE.
  useEffect(() => {
    if (!state.quizJobId) return;
    const offReady = sseBus.on('ai_quiz_ready', (frame) => {
      const data = frame as unknown as { job_id: string; questions?: WizardQuestion[] };
      if (data.job_id !== state.quizJobId || !Array.isArray(data.questions)) return;
      setAiQuestions(data.questions);
      toast.success(tAi('quizReady'));
      goTo(3);
    });
    const offFailed = sseBus.on('ai_quiz_failed', (frame) => {
      const data = frame as unknown as { job_id: string };
      if (data.job_id !== state.quizJobId) return;
      toast.error(tAi('quizFailed'));
      set('quizJobId', undefined);
    });
    return () => {
      offReady();
      offFailed();
    };
  }, [state.quizJobId, goTo, set, tAi]);

  const handleGenerate = useCallback(async () => {
    if (!state.selectedRole) return;
    try {
      const result = await generatePath.mutateAsync({
        goal: state.selectedRole.title,
        weekly_hours: state.weeklyHours,
        preferences: {
          is_free: state.freeContentOnly,
          format: state.format,
          language: state.language,
        },
        answers: state.answers,
      });
      const pathId = (result as { id?: number }).id;
      if (pathId) {
        toast.success(t('successMessage'));
        setOpen(false);
        router.push(`/learn/${pathId}`);
      }
    } catch {
      toast.error(t('errorMessage'));
    }
  }, [state, generatePath, router, t]);

  const progressPct = Math.round(((state.step - 1) / (STEP_COUNT - 1)) * 100);

  const stepTitle = useCallback(() => {
    switch (state.step) {
      case 1: return t('goalTitle');
      case 2: return t('preferencesTitle');
      case 3: return t('assessmentTitle');
      case 4: return tAi('resultsTitle');
      case 5: return t('summaryTitle');
    }
  }, [state.step, t, tAi]);

  const stepSubtitle = useCallback(() => {
    switch (state.step) {
      case 1: return t('goalSubtitle');
      case 2: return t('preferencesSubtitle');
      case 3: return t('assessmentSubtitle');
      case 4: return tAi('resultsSubtitle');
      case 5: return t('summarySubtitle');
    }
  }, [state.step, t, tAi]);

  return (
    <Dialog open={open} onOpenChange={handleOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="me-2 h-4 w-4" />
          {t('generatePath')}
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{stepTitle()}</DialogTitle>
          <DialogDescription>{stepSubtitle()}</DialogDescription>
        </DialogHeader>

        <div className="space-y-2">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span>{t('stepOf', { current: state.step, total: STEP_COUNT })}</span>
          </div>
          <div className="h-1 w-full rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-primary transition-all duration-300"
              style={{ width: `${progressPct}%` }}
            />
          </div>
        </div>

        <div className="py-2 min-h-[240px]">
          {state.step === 1 && (
            <GoalStep
              roles={roles}
              selectedRole={state.selectedRole}
              onSelect={(role) => set('selectedRole', role)}
              onClearSearch={() => set('searchQuery', '')}
              onGenerateQuiz={handleGenerateQuiz}
              quizGenerating={generateQuiz.isPending}
            />
          )}

          {state.step === 2 && (
            <PreferencesStep
              skillLevel={state.skillLevel}
              weeklyHours={state.weeklyHours}
              format={state.format}
              language={state.language}
              freeContentOnly={state.freeContentOnly}
              onSkillLevelChange={(v) => set('skillLevel', v)}
              onHoursChange={(v) => set('weeklyHours', v)}
              onFormatChange={(v) => set('format', v)}
              onLanguageChange={(v) => set('language', v)}
              onFreeContentToggle={() => set('freeContentOnly', !state.freeContentOnly)}
            />
          )}

          {state.step === 3 && (
            <AssessmentStep
              hasSkillProfile={hasSkillProfile}
              questions={questions}
              isLoading={questionsLoading}
              answers={state.answers}
              onAnswer={(questionId, optionIndex) =>
                set('answers', { ...state.answers, [questionId]: optionIndex })
              }
              onSkip={() => handleAssessmentContinue(false)}
              onStart={() => handleAssessmentContinue(true)}
            />
          )}

          {state.step === 4 && (
            <ResultsStep
              analysis={state.analysis ?? null}
              isPending={analysis.isPending}
              isError={analysis.isError}
              onContinue={() => goTo(5)}
            />
          )}

          {state.step === 5 && (
            <SummaryStep
              state={state}
              isPending={generatePath.isPending}
              isError={generatePath.isError}
              onGenerate={handleGenerate}
            />
          )}
        </div>

        <StepNavigation
          step={state.step}
          totalSteps={STEP_COUNT}
          canProceed={canProceed}
          onBack={() => goTo((state.step - 1) as Step)}
          onNext={() => goTo((state.step + 1) as Step)}
        />
      </DialogContent>
    </Dialog>
  );
}
