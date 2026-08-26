'use client';

import { useLocaleContext } from '@/i18n/provider';
import { Button } from '@/shared/ui/button';
import { Globe } from 'lucide-react';

export function LocaleSwitcher() {
  const { locale, setLocale } = useLocaleContext();

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={() => setLocale(locale === 'en' ? 'ar' : 'en')}
      className="gap-2"
    >
      <Globe className="h-4 w-4" />
      <span className="text-xs">{locale === 'en' ? 'AR' : 'EN'}</span>
    </Button>
  );
}
