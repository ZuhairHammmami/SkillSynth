'use client';

import { useState, useRef, useEffect } from 'react';
import { useTranslations, useLocale } from 'next-intl';
import { toast } from 'sonner';
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card';
import { Button } from '@/shared/ui/button';
import { PageLoading } from '@/shared/components/Loading';
import { TakeQuizDialog } from '@/shared/components/TakeQuizDialog';
import { useAnalyticsDashboard, useWeaknesses } from '@/shared/hooks/useAnalyticsApi';
import { useGeneratePracticeTest } from '@/shared/hooks/useAiApi';
import { useDashboard } from '@/shared/hooks/usePathApi';
import { useSSE } from '@/shared/hooks/useSSE';
import { sseBus } from '@/shared/lib/sseBus';
import { formatDate } from '@/shared/lib/utils';
import type { WeaknessEntry } from '@/types/api';
import { TrendingUp, BarChart3, GraduationCap, Target } from 'lucide-react';

interface QuizDialogState {
  open: boolean;
  skillId: number;
  skillName: string;
  assessmentId: number | null;
}

const QUIZ_CLOSED: QuizDialogState = {
  open: false,
  skillId: 0,
  skillName: '',
  assessmentId: null,
};

/** Student analytics dashboard: stat cards, learning velocity, paths
 * overview, recent activity and (SS-AI) a weaknesses panel that launches
 * AI-generated practice tests into TakeQuizDialog via SSE ai_test_ready.
 * Consumes useWeaknesses/useGeneratePracticeTest hooks and sseBus frames
 * forwarded by useSSE. */
export default function AnalyticsPage() {
  const t = useTranslations('analytics');
  const tAi = useTranslations('ai');
  const locale = useLocale();
  const { data: analytics, isLoading } = useAnalyticsDashboard();
  const { data: dashboard } = useDashboard();
  const { data: weaknessData } = useWeaknesses();
  const generateTest = useGeneratePracticeTest();
  const [quiz, setQuiz] = useState<QuizDialogState>(QUIZ_CLOSED);
  const pendingJobRef = useRef<string | null>(null);
  const awaitingSkillRef = useRef<{ skillId: number; skillName: string } | null>(null);
  useSSE();

  // Open TakeQuizDialog when the generated practice test lands over SSE.
  useEffect(() => {
    const off = sseBus.on('ai_test_ready', (frame) => {
      const data = frame as unknown as { job_id: string; assessment_id: number };
      if (!pendingJobRef.current || data.job_id !== pendingJobRef.current) return;
      pendingJobRef.current = null;
      const skill = awaitingSkillRef.current;
      awaitingSkillRef.current = null;
      toast.success(tAi('testReady'));
      if (!skill) return;
      setQuiz({
        open: true,
        skillId: skill.skillId,
        skillName: skill.skillName,
        assessmentId: data.assessment_id,
      });
    });
    return off;
  }, [tAi]);

  /** Request a 5-question AI practice test for one weak skill; the
   * resulting assessment id arrives asynchronously over SSE. Called by
   * the per-row practice-test buttons in the weaknesses panel. */
  const handlePracticeTest = async (w: WeaknessEntry) => {
    try {
      const { job_id } = await generateTest.mutateAsync({
        skill_id: w.skill_id,
        n_questions: 5,
      });
      pendingJobRef.current = job_id;
      awaitingSkillRef.current = { skillId: w.skill_id, skillName: w.skill_name };
      toast(tAi('generatingTest'));
    } catch (err) {
      const status = (err as { response?: { status?: number } }).response?.status;
      toast.error(status === 503 ? tAi('aiDisabled') : tAi('testFailed'));
    }
  };

  if (isLoading) return <PageLoading />;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{t('title')}</h1>
        <p className="text-sm text-muted-foreground mt-1">{t('subtitle')}</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground flex items-center gap-1">
              <BarChart3 className="h-4 w-4" /> {t('completion')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics?.completion_rate ?? 0}%</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground flex items-center gap-1">
              <GraduationCap className="h-4 w-4" /> {t('skillsMastered')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics?.mastered_skills ?? 0}</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-4 w-4" />
              {tAi('weaknessesTitle')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {(weaknessData?.weaknesses ?? []).length === 0 ? (
              <p className="text-sm text-muted-foreground">{tAi('noWeaknesses')}</p>
            ) : (
              <div className="grid gap-x-8 sm:grid-cols-2">
                {(weaknessData?.weaknesses ?? []).map((w) => (
                  <div key={w.skill_id} className="flex items-center justify-between gap-3 py-2.5">
                    <div className="min-w-0">
                      <p className="text-sm font-medium truncate">{w.skill_name}</p>
                      <p className="text-xs text-muted-foreground">
                        {tAi('levelLabel', { level: w.current_level })}
                        {w.gap != null && w.gap > 0
                          ? ` · ${tAi('gapToMastery', { gap: w.gap })}`
                          : ''}
                      </p>
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      className="shrink-0"
                      disabled={generateTest.isPending}
                      onClick={() => handlePracticeTest(w)}
                    >
                      {tAi('practiceTest')}
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              {t('learningVelocity')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {analytics?.learning_velocity ? (
              <div className="text-3xl font-bold">{analytics.learning_velocity.toFixed(1)}</div>
            ) : (
              <p className="text-sm text-muted-foreground">{t('learningVelocityEmpty')}</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t('pathsOverview')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">{t('activePaths')}</span>
                <span className="font-medium">{dashboard?.total_paths ?? 0}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">{t('stepsLabel')}</span>
                <span className="font-medium">{dashboard?.total_steps ?? 0}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">{t('completedLabel')}</span>
                <span className="font-medium">{dashboard?.completed_steps ?? 0}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">{t('remainingHours')}</span>
                <span className="font-medium">{dashboard?.remaining_hours ?? 0}h</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t('recentActivity')}</CardTitle>
          </CardHeader>
          <CardContent>
            {analytics?.recent_activity && (analytics.recent_activity as unknown[]).length > 0 ? (
              <div className="space-y-3">
                {(analytics.recent_activity as { type?: string; description?: string; date?: string }[]).slice(0, 5).map((act, i) => (
                  <div key={i} className="flex items-center gap-3 text-sm">
                    <div className="h-2 w-2 rounded-full bg-primary" />
                    <span className="flex-1">{act.description || act.type}</span>
                    <span className="text-xs text-muted-foreground">{act.date ? formatDate(act.date, locale) : ''}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">{t('noActivity')}</p>
            )}
          </CardContent>
        </Card>
      </div>

      <TakeQuizDialog
        open={quiz.open}
        onOpenChange={(o) => setQuiz((prev) => ({ ...prev, open: o }))}
        skillId={quiz.skillId}
        skillName={quiz.skillName}
        assessmentId={quiz.assessmentId}
      />
    </div>
  );
}
