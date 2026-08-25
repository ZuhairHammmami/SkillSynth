'use client';

import { useTranslations } from 'next-intl';
import { Badge } from '@/shared/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card';
import { PageLoading } from '@/shared/components/Loading';
import { useSkillGrowth } from '@/shared/hooks/useAnalyticsApi';
import { GraduationCap } from 'lucide-react';

interface SkillEntry {
  skill: string;
  level: number;
  status: string;
}

const MAX_SKILLS = 6;

type StatusKey = 'mastered' | 'learning' | 'notStarted';

function statusVariant(status: string): 'success' | 'warning' | 'outline' {
  if (status === 'mastered') return 'success';
  if (status === 'learning') return 'warning';
  return 'outline';
}

function statusKey(status: string): StatusKey {
  if (status === 'mastered') return 'mastered';
  if (status === 'learning') return 'learning';
  return 'notStarted';
}

export function TopSkills() {
  const t = useTranslations('profile.skills');
  const { data, isLoading } = useSkillGrowth();

  if (isLoading) return <PageLoading />;

  const skills = ((data?.skills as SkillEntry[]) ?? []).slice(0, MAX_SKILLS);

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-base">
          <GraduationCap className="h-4 w-4" /> {t('title')}
        </CardTitle>
        <p className="text-sm font-normal text-muted-foreground">{t('subtitle')}</p>
      </CardHeader>
      <CardContent>
        {skills.length === 0 ? (
          <p className="text-sm text-muted-foreground">{t('emptyDesc')}</p>
        ) : (
          <div className="space-y-3">
            {skills.map((entry) => (
              <div key={entry.skill} className="flex items-center justify-between gap-3">
                <span className="truncate text-sm font-medium">{entry.skill}</span>
                <div className="flex shrink-0 items-center gap-2">
                  <span className="text-xs text-muted-foreground">{t('level')} {entry.level}</span>
                  <Badge variant={statusVariant(entry.status)}>{t(statusKey(entry.status))}</Badge>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
