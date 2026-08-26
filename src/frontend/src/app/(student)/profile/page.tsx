'use client';

import { useTranslations } from 'next-intl';
import { Card, CardContent } from '@/shared/ui/card';
import { Avatar, AvatarFallback } from '@/shared/ui/avatar';
import { PageLoading } from '@/shared/components/Loading';
import { TopSkills } from './TopSkills';
import { useProfile } from '@/shared/hooks/useAuthApi';
import { getInitials, formatDate } from '@/shared/lib/utils';
import { Calendar } from 'lucide-react';

export default function ProfilePage() {
  const t = useTranslations('profile');
  const { data: profile, isLoading } = useProfile();

  if (isLoading) return <PageLoading />;
  if (!profile) return <div className="text-center py-16">{t('notFound')}</div>;

  return (
    <div className="max-w-2xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{t('title')}</h1>
        <p className="text-sm text-muted-foreground mt-1">{t('subtitle')}</p>
      </div>

      <Card>
        <CardContent className="p-6">
          <div className="flex items-center gap-6">
            <Avatar className="h-16 w-16">
              <AvatarFallback className="text-lg">
                {profile.full_name ? getInitials(profile.full_name) : profile.email.slice(0, 2).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div>
              <h2 className="text-xl font-semibold">{profile.full_name || t('unnamedUser')}</h2>
              <p className="text-sm text-muted-foreground">{profile.email}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <TopSkills />

      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-2">
            <Calendar className="h-3 w-3 text-muted-foreground" />
            <span className="text-xs text-muted-foreground">{t('joined')}</span>
            <span className="ms-auto text-sm font-medium">
              {profile.created_at ? formatDate(profile.created_at) : 'N/A'}
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
