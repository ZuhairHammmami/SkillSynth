/** Reactive hand-rolled i18n (Svelte 5 runes). Replaces the cookie-reading
 *  version in index.ts so translations re-render instantly when the locale
 *  changes — no page reload. Reads the shared reactive localeStore mirror. */
import en from './messages/en.json';
import ar from './messages/ar.json';
import { localeStore, type Locale } from '$lib/stores/locale';

type Dict = Record<string, any>;
const dicts: Record<Locale, Dict> = { en: en as Dict, ar: ar as Dict };
export const locales = ['en', 'ar'] as const;

/** Reactive mirror of the active locale. A rune object (not a reassigned
 *  binding) so the subscription can mutate a property without tripping the
 *  Svelte 5 "can't reassign const $state" error. Subscribing to localeStore
 *  makes any component that calls t() depend on it, so switches re-render. */
export const i18n = $state<{ locale: Locale }>({ locale: 'en' });
localeStore.subscribe((v) => {
  i18n.locale = v.locale;
});

function getPath(d: Dict, key: string): string | undefined {
  return key.split('.').reduce<any>((o, k) => (o == null ? undefined : o[k]), d);
}

/** Translate a key, interpolating {placeholders}. Falls back to English then to the key. */
export function t(key: string, params?: Record<string, string | number>): string {
  let str: string = getPath(dicts[i18n.locale], key) ?? getPath(dicts.en, key) ?? key;
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      str = str.replace(new RegExp('\\{' + k + '\\}', 'g'), String(v));
    }
  }
  return str;
}
