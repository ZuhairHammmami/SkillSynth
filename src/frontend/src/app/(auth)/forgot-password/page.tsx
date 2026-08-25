'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { Button } from '@/shared/ui/button';
import { Input } from '@/shared/ui/input';
import { Logo } from '@/shared/components/Logo';
import { useForgotPassword } from '@/shared/hooks/useAuthApi';
import { ArrowLeft, CheckCircle } from 'lucide-react';

export default function ForgotPasswordPage() {
  const t = useTranslations('forgotPasswordPage');
  const forgotMutation = useForgotPassword();
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);
  const [resetToken, setResetToken] = useState<string | undefined>();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await forgotMutation.mutateAsync(email) as { reset_token?: string };
    setResetToken(res.reset_token);
    setSent(true);
  };

  if (sent) {
    return (
      <div className="text-center">
        <div className="mb-6 inline-flex items-center justify-center h-12 w-12 rounded-full bg-emerald-50 text-emerald-600">
          <CheckCircle className="h-6 w-6" />
        </div>
        <h1 className="text-2xl font-bold tracking-tight mb-2">{t('checkEmailTitle')}</h1>
        <p className="text-sm text-muted-foreground mb-6">{t('checkEmailDesc')}</p>
        {resetToken && (
          <div className="mb-6 rounded-lg border bg-muted/50 p-4 text-left space-y-2">
            <p className="text-xs font-medium text-muted-foreground">{t('devResetNote')}</p>
            <Link
              href={`/reset-password?token=${encodeURIComponent(resetToken)}`}
              className="block text-sm font-semibold text-primary break-all hover:underline"
            >
              {t('devResetLink')}
            </Link>
          </div>
        )}
        <Button variant="outline" asChild>
          <Link href="/login"><ArrowLeft className="ms-2 h-4 w-4" />{t('backToSignIn')}</Link>
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
        <div className="space-y-2">
          <label htmlFor="email" className="text-sm font-medium">{t('emailLabel')}</label>
          <Input id="email" type="email" placeholder={t('emailPlaceholder')} value={email} onChange={(e) => setEmail(e.target.value)} required />
        </div>
        <Button type="submit" className="w-full" disabled={forgotMutation.isPending}>
          {forgotMutation.isPending ? t('sending') : t('sendReset')}
        </Button>
      </form>

      <p className="text-center text-sm text-muted-foreground mt-6">
        <Link href="/login" className="hover:text-primary">
          <ArrowLeft className="inline h-3 w-3 ms-1" />{t('backToSignIn')}
        </Link>
      </p>
    </div>
  );
}
