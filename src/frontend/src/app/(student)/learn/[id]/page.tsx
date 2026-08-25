'use client';

import { useTranslations } from 'next-intl';
import { useParams, useRouter } from 'next/navigation';
import { Button } from '@/shared/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/shared/ui/card';
import { Badge } from '@/shared/ui/badge';
import { PageLoading } from '@/shared/components/Loading';
import { usePathDetail, useCompleteStep, useUndoCompleteStep, useDeletePath } from '@/shared/hooks/usePathApi';
import { useSSE } from '@/shared/hooks/useSSE';
import { BookOpen, Clock, CheckCircle, Circle, ArrowLeft, Trash2, ExternalLink } from 'lucide-react';

export default function PathDetailPage() {
  const t = useTranslations('pathDetailPage');
  const pd = useTranslations('pathDetail');
  const params = useParams();
  const router = useRouter();
  const id = Number(params.id);
  const { data: path, isLoading } = usePathDetail(id);
  useSSE();
  const completeStep = useCompleteStep();
  const undoStep = useUndoCompleteStep();
  const deletePath = useDeletePath();

  if (isLoading) return <PageLoading />;
  if (!path) return <div className="text-center py-16">{t('notFound')}</div>;

  const completed = path.steps.filter((s) => s.is_completed).length;
  const total = path.steps.length;
  const pct = total > 0 ? Math.round((completed / total) * 100) : 0;

  const handleDelete = async () => {
    if (confirm(t('deleteConfirm'))) {
      await deletePath.mutateAsync(id);
      router.push('/learn');
    }
  };

  return (
    <div className="max-w-3xl space-y-8">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => router.push('/learn')}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight">{path.title}</h1>
            {path.goal_job_role && <Badge variant="secondary">{path.goal_job_role}</Badge>}
          </div>
          {path.description && (
            <p className="text-sm text-muted-foreground mt-1">{path.description}</p>
          )}
        </div>
        <Button variant="ghost" size="icon" onClick={handleDelete} className="text-destructive">
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>

      <div className="grid gap-4 grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">{t('progress')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{pct}%</div>
            <p className="text-xs text-muted-foreground">{completed}/{total} {pd('steps')}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">{t('duration')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{path.total_estimated_hours}{pd('hoursShort')}</div>
            <p className="text-xs text-muted-foreground">{path.total_estimated_weeks} {pd('weeks')}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">{t('skillsTitle')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{path.skills?.length || path.skill_ids?.length || 0}</div>
            <p className="text-xs text-muted-foreground">{t('toMaster')}</p>
          </CardContent>
        </Card>
      </div>

      <div className="h-2 w-full rounded-full bg-muted">
        <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${pct}%` }} />
      </div>

      <div className="space-y-3">
        <h2 className="text-lg font-semibold">{t('stepsTitle')}</h2>
        {path.steps
          .sort((a, b) => a.step_number - b.step_number)
          .map((step) => (
            <Card key={step.id} className={step.is_completed ? 'border-primary/20 bg-primary/5' : ''}>
              <CardContent className="p-4">
                <div className="flex items-start gap-4">
                  <button
                    onClick={() => step.is_completed ? undoStep.mutateAsync(step.id) : completeStep.mutateAsync(step.id)}
                    className="mt-1"
                  >
                    {step.is_completed ? (
                      <CheckCircle className="h-5 w-5 text-primary" />
                    ) : (
                      <Circle className="h-5 w-5 text-muted-foreground" />
                    )}
                  </button>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-muted-foreground font-mono">{t('stepLabel')} {step.step_number}</span>
                      {step.is_completed && <Badge variant="success" className="text-[10px]">{t('done')}</Badge>}
                    </div>
                    <h3 className="font-medium mt-1">{step.title}</h3>
                    {step.content && <p className="text-sm text-muted-foreground mt-1">{step.content}</p>}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
      </div>

      {path.skills && path.skills.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold">{t('skillsSection')}</h2>
          <div className="flex flex-wrap gap-2">
            {path.skills.map((skill) => (
              <Badge key={skill.id} variant="outline">{skill.name}</Badge>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
