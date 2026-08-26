'use client';

import { useTranslations } from 'next-intl';

const features = ['feature1', 'feature2', 'feature3', 'feature4'];

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  const t = useTranslations('authLayout');

  return (
    <div className="flex min-h-screen">
      <div className="flex flex-1 items-center justify-center px-4 py-12">
        <div className="w-full max-w-sm">{children}</div>
      </div>
      <div className="hidden lg:flex lg:w-1/2 bg-muted items-center justify-center p-12">
        <div className="max-w-md">
          <h2 className="text-3xl font-bold tracking-tight mb-4">{t('title')}</h2>
          <p className="text-muted-foreground leading-relaxed">{t('subtitle')}</p>
          <div className="mt-8 grid grid-cols-2 gap-4">
            {features.map((key) => (
              <div key={key} className="rounded-lg border bg-card p-4 text-sm font-medium">{t(key)}</div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
