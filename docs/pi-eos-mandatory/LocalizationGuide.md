# Localization Guide

## i18n Architecture
- **Library**: next-intl v3.17+
- **Locales**: English (`en`), Arabic (`ar`)
- **Default**: `en`
- **Detection**: `NEXT_LOCALE` cookie → `Accept-Language` header → `en`
- **Direction**: `en`="ltr", `ar`="rtl"

## Translation Files
```
src/frontend/src/i18n/
├── config.ts         # locales, defaultLocale, localeLabels, localeDirections
├── hooks.ts          # useLocaleContext wrapper
├── provider.tsx      # LocaleProvider (detection, switching)
├── request.ts        # getMessages for server components
├── root-provider.tsx # Root provider wrapper
└── messages/
    ├── en.json       # 35KB English translations
    └── ar.json       # 46KB Arabic translations
```

## Usage
```tsx
'use client';
import { useTranslations } from 'next-intl';

function MyComponent() {
  const t = useTranslations('dashboard');
  return <h1>{t('title')}</h1>;
}
```

## Rules
1. **Zero hardcoded strings** — All user-facing text must use `t()`
2. **Key organization** → `['admin', 'student', 'auth', 'wizard', 'common', 'errors']`
3. **Dynamic data** → Never in translation files; use `t('key', {name: user.name})`
4. **RTL-first** → `<html lang="ar" dir="rtl">` by default; `dir` switches dynamically
5. **Fonts** → Tajawal for Arabic, system-ui for English fallback

## Language Switch
`LocaleSwitcher` component (Globe icon) toggles between AR/EN. Updates cookie, triggers re-render.
