'use client';

import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { Button } from '@/shared/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card';
import { Badge } from '@/shared/ui/badge';
import { PageLoading } from '@/shared/components/Loading';
import { NewPathDialog } from '@/shared/components/NewPathDialog';
import { usePaths } from '@/shared/hooks/usePathApi';
import { Compass, Plus, BookOpen, Clock, ArrowRight } from 'lucide-react';

export default function LearnPage() {
  const t = useTranslations('learnPage');
  const { data: paths, isLoading } = usePaths();

  if (isLoading) return <PageLoading />;

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{t('title')}</h1>
          <p className="text-sm text-muted-foreground mt-1">{t('subtitle')}</p>
        </div>
        <NewPathDialog />
      </div>

      {paths && paths.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {paths.map((path) => {
            const completed = path.steps.filter((s) => s.is_completed).length;
            const total = path.steps.length;
            const pct = total > 0 ? Math.round((completed / total) * 100) : 0;
            return (
              <Link key={path.id} href={`/learn/${path.id}`}>
                <Card className="h-full hover:shadow-md transition-shadow cursor-pointer">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <CardTitle className="text-base">{path.title}</CardTitle>
                      <Compass className="h-4 w-4 text-muted-foreground" />
                    </div>
                    {path.goal_job_role && <Badge variant="secondary" className="w-fit">{path.goal_job_role}</Badge>}
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {path.description && <p className="text-sm text-muted-foreground line-clamp-2">{path.description}</p>}
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1"><BookOpen className="h-3 w-3" />{t('stepsCount', { count: total })}</span>
                      <span className="flex items-center gap-1"><Clock className="h-3 w-3" />{t('hoursCount', { count: path.total_estimated_hours })}</span>
                    </div>
                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span>{t('completePercent', { pct })}</span>
                        <span>{t('stepProgress', { completed, total })}</span>
                      </div>
                      <div className="h-1.5 w-full rounded-full bg-muted">
                        <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                    <div className="flex items-center text-sm font-medium text-primary">
                      {t('continue')} <ArrowRight className="ms-1 h-3 w-3" />
                    </div>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-16">
          <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-muted mb-6">
            <Compass className="h-8 w-8 text-muted-foreground" />
          </div>
          <h2 className="text-xl font-semibold mb-2">{t('emptyTitle')}</h2>
          <p className="text-sm text-muted-foreground mb-6 max-w-md mx-auto">{t('emptyDesc')}</p>
          <NewPathDialog />
        </div>
      )}
    </div>
  );
}
