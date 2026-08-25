'use client';

import Link from 'next/link';
import { useTranslations, useLocale } from 'next-intl';
import { Button } from '@/shared/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card';
import { Badge } from '@/shared/ui/badge';
import { PageLoading } from '@/shared/components/Loading';
import { useDashboard, usePaths } from '@/shared/hooks/usePathApi';
import { useAnalyticsDashboard } from '@/shared/hooks/useAnalyticsApi';
import { useSSE } from '@/shared/hooks/useSSE';
import { formatDate } from '@/shared/lib/utils';
import { Plus, TrendingUp, Flame, Clock, BookOpen } from 'lucide-react';

export default function DashboardPage() {
  const t = useTranslations('dashboardPage');
  const locale = useLocale();
  const { data: dashboard, isLoading } = useDashboard();
  const { data: paths, isLoading: pathsLoading } = usePaths();
  const { data: analytics } = useAnalyticsDashboard();
  useSSE();

  if (isLoading || pathsLoading) return <PageLoading />;

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{t('title')}</h1>
          <p className="text-sm text-muted-foreground mt-1">{t('subtitle')}</p>
        </div>
        <Button asChild>
          <Link href="/learn"><Plus className="ms-2 h-4 w-4" />{t('newPath')}</Link>
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">{t('completionRate')}</CardTitle>
            <TrendingUp className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{dashboard?.completion_percentage ?? 0}%</div>
            <p className="text-xs text-muted-foreground mt-1">{dashboard?.completed_steps ?? 0}{t('stepsOf')}{dashboard?.total_steps ?? 0}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">{t('learningHours')}</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{dashboard?.total_hours ?? 0}h</div>
            <p className="text-xs text-muted-foreground mt-1">{dashboard?.remaining_hours ?? 0}h {t('remaining')}</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
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
              <p className="text-sm text-muted-foreground">{t('noRecentActivity')}</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t('yourPaths')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {paths && paths.length > 0 ? (
              paths.slice(0, 3).map((path) => {
                const completed = path.steps.filter((s) => s.is_completed).length;
                const total = path.steps.length;
                const pct = total > 0 ? Math.round((completed / total) * 100) : 0;
                return (
                  <Link key={path.id} href={`/learn/${path.id}`} className="block rounded-lg border p-4 hover:bg-muted/50 transition-colors">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium text-sm">{path.title}</h3>
                      <Badge variant="secondary" className="text-xs">{pct}%</Badge>
                    </div>
                    <div className="flex gap-4 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1"><BookOpen className="h-3 w-3" />{total} {t('steps')}</span>
                      <span>{completed} {t('completed')}</span>
                    </div>
                    <div className="mt-2 h-1.5 w-full rounded-full bg-muted">
                      <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${pct}%` }} />
                    </div>
                  </Link>
                );
              })
            ) : (
              <div className="text-center py-6">
                <p className="text-sm text-muted-foreground mb-4">{t('noPaths')}</p>
                <Button size="sm" asChild>
                  <Link href="/learn">{t('createFirstPath')}</Link>
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
