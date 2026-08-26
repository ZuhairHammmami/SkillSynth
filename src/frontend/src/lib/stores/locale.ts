/** Locale state for the bilingual (AR/EN) experience. Cookie-driven so it
 *  survives reloads; sets <html lang/dir> for instant RTL mirroring. */
import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { getCookie, setCookie } from '$lib/util';

export type Locale = 'en' | 'ar';
export type Dir = 'ltr' | 'rtl';

export const localeStore = writable<{ locale: Locale; dir: Dir }>({ locale: 'en', dir: 'ltr' });

export function localeDir(locale: Locale): Dir {
  return locale === 'ar' ? 'rtl' : 'ltr';
}

export function initLocale(): void {
  const l = (browser ? getCookie('LOCALE') : 'en') as Locale;
  const locale = l === 'ar' ? 'ar' : 'en';
  localeStore.set({ locale, dir: localeDir(locale) });
  if (browser) {
    document.documentElement.lang = locale;
    document.documentElement.dir = localeDir(locale);
  }
}

export function setLocale(locale: Locale): void {
  setCookie('LOCALE', locale, 365);
  localeStore.set({ locale, dir: localeDir(locale) });
  if (browser) {
    document.documentElement.lang = locale;
    document.documentElement.dir = localeDir(locale);
  }
}
