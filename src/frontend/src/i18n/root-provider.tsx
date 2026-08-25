import { defaultLocale, locales, type Locale } from './config';
import { LocaleProvider } from './provider';
import enMessages from './messages/en.json';
import arMessages from './messages/ar.json';

const messageMap: Record<Locale, Record<string, unknown>> = {
  en: enMessages as Record<string, unknown>,
  ar: arMessages as Record<string, unknown>,
};

export function RootProvider({
  locale,
  children,
}: {
  locale: string;
  children: React.ReactNode;
}) {
  const resolvedLocale: Locale = locales.includes(locale as Locale) ? (locale as Locale) : defaultLocale;
  const messages = messageMap[resolvedLocale] || messageMap[defaultLocale];

  return (
    <LocaleProvider initialLocale={resolvedLocale} messages={messages}>
      {children}
    </LocaleProvider>
  );
}
