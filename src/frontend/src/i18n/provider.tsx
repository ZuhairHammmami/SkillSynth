'use client';

import { createContext, useContext, useEffect, useState, useCallback, useRef, type ReactNode } from 'react';
import { NextIntlClientProvider, type AbstractIntlMessages } from 'next-intl';
import { defaultLocale, localeDirections, type Locale, locales } from './config';

interface LocaleContextType {
  locale: Locale;
  direction: 'ltr' | 'rtl';
  setLocale: (locale: Locale) => void;
}

const LocaleContext = createContext<LocaleContextType>({
  locale: defaultLocale,
  direction: 'ltr',
  setLocale: () => {},
});

export function useLocaleContext() {
  return useContext(LocaleContext);
}

const LOCALE_COOKIE = 'NEXT_LOCALE';

function getCookie(name: string): string | undefined {
  if (typeof document === 'undefined') return undefined;
  const match = document.cookie.match(new RegExp(`(?:^|;\\s*)${name}=([^;]*)`));
  return match?.[1];
}

function setCookie(name: string, value: string) {
  document.cookie = `${name}=${value};path=/;max-age=31536000;SameSite=Lax`;
}

async function loadMessages(locale: Locale): Promise<Record<string, unknown>> {
  try {
    const messages = await import(`./messages/${locale}.json`);
    return messages.default;
  } catch {
    const fallback = await import(`./messages/${defaultLocale}.json`);
    return fallback.default;
  }
}

interface LocaleProviderProps {
  initialLocale: Locale;
  messages: Record<string, unknown>;
  children: ReactNode;
}

export function LocaleProvider({ initialLocale, messages: initialMessages, children }: LocaleProviderProps) {
  const [locale, setLocaleState] = useState<Locale>(initialLocale);
  const [messages, setMessages] = useState<Record<string, unknown>>(initialMessages ?? {});

  const setLocale = useCallback(async (newLocale: Locale) => {
    setLocaleState(newLocale);
    setCookie(LOCALE_COOKIE, newLocale);
    document.documentElement.lang = newLocale;
    document.documentElement.dir = localeDirections[newLocale];
    const newMessages = await loadMessages(newLocale);
    setMessages(newMessages);
  }, []);

  useEffect(() => {
    const saved = getCookie(LOCALE_COOKIE);
    if (saved && locales.includes(saved as Locale) && saved !== locale) {
      setLocaleState(saved as Locale);
      loadMessages(saved as Locale).then(setMessages);
    }
    document.documentElement.lang = locale;
    document.documentElement.dir = localeDirections[locale];
  }, [locale]);

  const direction = localeDirections[locale];
  const now = useRef(new Date());

  return (
    <LocaleContext.Provider value={{ locale, direction, setLocale }}>
      <NextIntlClientProvider locale={locale} messages={messages as AbstractIntlMessages} timeZone="UTC" now={now.current}>
        {children}
      </NextIntlClientProvider>
    </LocaleContext.Provider>
  );
}
