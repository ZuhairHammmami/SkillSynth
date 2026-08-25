import { defaultLocale, type Locale, locales } from './config';

export function getLocaleFromCookie(cookieValue?: string): Locale {
  if (cookieValue && locales.includes(cookieValue as Locale)) {
    return cookieValue as Locale;
  }
  return defaultLocale;
}

export async function loadMessages(locale: Locale) {
  try {
    const messages = await import(`./messages/${locale}.json`);
    return messages.default;
  } catch {
    const fallback = await import(`./messages/${defaultLocale}.json`);
    return fallback.default;
  }
}

export function isLocale(value: string): value is Locale {
  return locales.includes(value as Locale);
}
