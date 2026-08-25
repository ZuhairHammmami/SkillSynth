'use client';

import { useTranslations, useLocale } from 'next-intl';
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card';
import { PageLoading } from '@/shared/components/Loading';
import { useAnalyticsDashboard } from '@/shared/hooks/useAnalyticsApi';
import { useDashboard } from '@/shared/hooks/usePathApi';
import { useSSE } from '@/shared/hooks/useSSE';
import { formatDate } from '@/shared/lib/utils';
import { TrendingUp, BarChart3, GraduationCap } from 'lucide-react';

export default function AnalyticsPage() {
  const t = useTranslations('analytics');
  const locale = useLocale();
  const { data: analytics, isLoading } = useAnalyticsDashboard();
  const { data: dashboard } = useDashboard();
  useSSE();

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
    </div>
  );
}
