'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { Button } from '@/shared/ui/button';
import { Input } from '@/shared/ui/input';
import { Logo } from '@/shared/components/Logo';
import { useResetPassword } from '@/shared/hooks/useAuthApi';
import { ArrowLeft, CheckCircle } from 'lucide-react';

export default function ResetPasswordPage() {
  const t = useTranslations('resetPasswordPage');
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get('token') || '';
  const resetMutation = useResetPassword();
  const [password, setPassword] = useState('');
  const [done, setDone] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await resetMutation.mutateAsync({ token, new_password: password });
      setDone(true);
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail || t('errorFailed'));
    }
  };

  if (done) {
    return (
      <div className="text-center">
        <div className="mb-6 inline-flex items-center justify-center h-12 w-12 rounded-full bg-emerald-50 text-emerald-600">
          <CheckCircle className="h-6 w-6" />
        </div>
        <h1 className="text-2xl font-bold tracking-tight mb-2">{t('successTitle')}</h1>
        <p className="text-sm text-muted-foreground mb-6">{t('successDesc')}</p>
        <Button asChild>
          <Link href="/login">{t('signIn')}</Link>
        </Button>
      </div>
    );
  }

  if (!token) {
    return (
      <div className="text-center">
        <h1 className="text-2xl font-bold tracking-tight mb-2">{t('invalidTitle')}</h1>
        <p className="text-sm text-muted-foreground mb-6">{t('invalidDesc')}</p>
        <Button variant="outline" asChild>
          <Link href="/forgot-password"><ArrowLeft className="ms-2 h-4 w-4" />{t('requestNew')}</Link>
        </Button>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <Logo />
        <h1 className="text-2xl font-bold tracking-tight mt-6">{t('title')}</h1>
        <p className="text-sm text-muted-foreground mt-2">{t('subtitle')}</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="rounded-md border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive">{error}</div>
        )}
        <div className="space-y-2">
          <label htmlFor="password" className="text-sm font-medium">{t('newPasswordLabel')}</label>
          <Input id="password" type="password" placeholder={t('passwordPlaceholder')} value={password} onChange={(e) => setPassword(e.target.value)} required autoComplete="new-password" />
        </div>
        <Button type="submit" className="w-full" disabled={resetMutation.isPending}>
          {resetMutation.isPending ? t('resetting') : t('resetPassword')}
        </Button>
      </form>
    </div>
  );
}
