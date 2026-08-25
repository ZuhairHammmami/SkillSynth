'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { Button } from '@/shared/ui/button';
import { Input } from '@/shared/ui/input';
import { Logo } from '@/shared/components/Logo';
import { useAuth } from '@/shared/hooks/useAuthApi';
import { ArrowRight } from 'lucide-react';

export default function LoginPage() {
  const t = useTranslations('loginPage');
  const router = useRouter();
  const { loginMutation } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await loginMutation.mutateAsync({ email, password });
      router.push('/dashboard');
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail || t('errorLoginFailed'));
    }
  };

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
          <label htmlFor="email" className="text-sm font-medium">{t('emailLabel')}</label>
          <Input id="email" type="email" placeholder={t('emailPlaceholder')} value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" />
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label htmlFor="password" className="text-sm font-medium">{t('passwordLabel')}</label>
            <Link href="/forgot-password" className="text-xs text-muted-foreground hover:text-primary">{t('forgotPassword')}</Link>
          </div>
          <Input id="password" type="password" placeholder={t('passwordPlaceholder')} value={password} onChange={(e) => setPassword(e.target.value)} required autoComplete="current-password" />
        </div>

        <Button type="submit" className="w-full" disabled={loginMutation.isPending}>
          {loginMutation.isPending ? t('signingIn') : t('signIn')}
        </Button>
      </form>

      <p className="text-center text-sm text-muted-foreground mt-6">
        {t('noAccount')}{' '}
        <Link href="/register" className="text-primary hover:underline font-medium">
          {t('createOne')} <ArrowRight className="inline h-3 w-3" />
        </Link>
      </p>
    </div>
  );
}
