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

export default function RegisterPage() {
  const t = useTranslations('registerPage');
  const router = useRouter();
  const { registerMutation } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await registerMutation.mutateAsync({ email, password, full_name: name || undefined });
      router.push('/login');
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail || t('errorFailed'));
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
          <label htmlFor="name" className="text-sm font-medium">{t('nameLabel')} <span className="text-muted-foreground">{t('nameOptional')}</span></label>
          <Input id="name" type="text" placeholder={t('namePlaceholder')} value={name} onChange={(e) => setName(e.target.value)} />
        </div>

        <div className="space-y-2">
          <label htmlFor="email" className="text-sm font-medium">{t('emailLabel')}</label>
          <Input id="email" type="email" placeholder={t('emailPlaceholder')} value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" />
        </div>

        <div className="space-y-2">
          <label htmlFor="password" className="text-sm font-medium">{t('passwordLabel')}</label>
          <Input id="password" type="password" placeholder={t('passwordPlaceholder')} value={password} onChange={(e) => setPassword(e.target.value)} required autoComplete="new-password" />
          <p className="text-xs text-muted-foreground">{t('passwordHint')}</p>
        </div>

        <Button type="submit" className="w-full" disabled={registerMutation.isPending}>
          {registerMutation.isPending ? t('creating') : t('create')}
        </Button>
      </form>

      <p className="text-center text-sm text-muted-foreground mt-6">
        {t('hasAccount')}{' '}
        <Link href="/login" className="text-primary hover:underline font-medium">
          {t('signIn')} <ArrowRight className="inline h-3 w-3" />
        </Link>
      </p>
    </div>
  );
}
