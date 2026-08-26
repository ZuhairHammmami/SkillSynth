'use client';

import { useTranslations } from 'next-intl';
import { useState } from 'react';
import { Button } from '@/shared/ui/button';
import { Input } from '@/shared/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/shared/ui/card';
import { PageLoading } from '@/shared/components/Loading';
import { useProfile, useUpdateProfile, useChangePassword } from '@/shared/hooks/useAuthApi';

export default function SettingsPage() {
  const t = useTranslations('settingsPage');
  const changePw = useTranslations('changePassword');
  const updatePro = useTranslations('updateProfile');
  const common = useTranslations('common');
  const { data: profile, isLoading } = useProfile();
  const updateProfile = useUpdateProfile();
  const changePassword = useChangePassword();
  const [name, setName] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [nameUpdated, setNameUpdated] = useState(false);
  const [passwordUpdated, setPasswordUpdated] = useState(false);

  if (isLoading) return <PageLoading />;
  if (!profile) return <div className="text-center py-16">{t('notFound')}</div>;

  const handleUpdateName = async () => {
    if (!name.trim()) return;
    await updateProfile.mutateAsync({ full_name: name });
    setNameUpdated(true);
    setTimeout(() => setNameUpdated(false), 2000);
  };

  const handleChangePassword = async () => {
    if (!currentPassword || !newPassword) return;
    await changePassword.mutateAsync({ current_password: currentPassword, new_password: newPassword });
    setPasswordUpdated(true);
    setCurrentPassword('');
    setNewPassword('');
    setTimeout(() => setPasswordUpdated(false), 2000);
  };

  return (
    <div className="max-w-2xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{t('title')}</h1>
        <p className="text-sm text-muted-foreground mt-1">{t('subtitle')}</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('profileTitle')}</CardTitle>
          <CardDescription>{t('profileDesc')}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">{t('fullName')}</label>
            <Input
              placeholder={profile.full_name || t('fullName')}
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <Button onClick={handleUpdateName} disabled={updateProfile.isPending || !name.trim()}>
            {updateProfile.isPending ? updatePro('saving') : nameUpdated ? t('saved') : common('save')}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t('passwordTitle')}</CardTitle>
          <CardDescription>{t('passwordDesc')}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">{changePw('currentPasswordLabel')}</label>
            <Input
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">{changePw('newPasswordLabel')}</label>
            <Input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
            />
          </div>
          <Button onClick={handleChangePassword} disabled={changePassword.isPending || !currentPassword || !newPassword}>
            {changePassword.isPending ? changePw('changing') : passwordUpdated ? t('updated') : changePw('changeButton')}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t('accountTitle')}</CardTitle>
          <CardDescription>{t('accountDesc')}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">{updatePro('emailLabel')}</span>
            <span>{profile.email}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">{t('role')}</span>
            <span>{profile.is_admin ? t('admin') : t('student')}</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
