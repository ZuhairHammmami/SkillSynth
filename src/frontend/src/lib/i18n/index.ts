/** Hand-rolled i18n. Replaces next-intl. Reads the cookie-driven locale and
 *  resolves dot-path keys from the ported message catalogs. */
import en from './messages/en.json';
import ar from './messages/ar.json';
import { browser } from '$app/environment';
import { getCookie } from '$lib/util';
import type { Locale } from '$lib/stores/locale';

type Dict = Record<string, any>;
const dicts: Record<Locale, Dict> = { en: en as Dict, ar: ar as Dict };
export const locales = ['en', 'ar'] as const;

function getPath(d: Dict, key: string): string | undefined {
  return key.split('.').reduce<any>((o, k) => (o == null ? undefined : o[k]), d);
}

/** Translate a key, interpolating {placeholders}. Falls back to English then to the key. */
export function t(key: string, params?: Record<string, string | number>): string {
  const loc = (browser ? getCookie('LOCALE') : 'en') as Locale;
  let str: string = getPath(dicts[loc], key) ?? getPath(dicts.en, key) ?? key;
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      str = str.replace(new RegExp('\\{' + k + '\\}', 'g'), String(v));
    }
  }
  return str;
}
