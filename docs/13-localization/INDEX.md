# SS-EDS: Localization (i18n)

## Purpose
Document the 100% bilingual AR/EN localization strategy. Every user-facing string passes through next-intl's `t()` function. No hardcoded Arabic or English text exists in any component. RTL/LTR is dynamic based on cookie-detected locale.

## Responsibilities
- Maintain next-intl message files (`en.json`, `ar.json`) with matching key structures
- Implement locale detection from `NEXT_LOCALE` cookie with `Accept-Language` fallback
- Provide `LocaleSwitcher` component showing the opposite language name
- Format dates, numbers, and plurals per locale
- Ensure all components use logical CSS properties for RTL compatibility

## Inputs
- UX copy for all screens (English source, Arabic translation)
- Date/time/number formatting rules per locale
- CSS logical property polyfills

## Outputs
- Locale message files with matching keys
- Locale config (`locales`, `defaultLocale`, `localeLabels`, `localeDirections`)
- Locale request handler (`getLocaleFromCookie`, `loadMessages`)
- Root provider + i18n provider wrapping the app

## Dependencies
- 08-frontend (RootLayout reads cookie, sets lang + dir)
- 20-ui-system (typography, logical CSS properties)

## Locale Detection Flow
```
HTTP Request → Read NEXT_LOCALE cookie → Valid? → Use as active locale
                                            ↓ No
                                     Read Accept-Language header → Match locale? → Use match
                                                                              ↓ No match
                                                                        Default to 'en'
                                                                              ↓
                                                                  Set NEXT_LOCALE cookie
                                                                              ↓
                                                           Render <html lang={locale} dir={dir}>
```

## Locale Config
```typescript
// src/i18n/config.ts
locales = ['en', 'ar']
defaultLocale = 'en'
localeLabels = { en: 'English', ar: 'العربية' }
localeDirections = { en: 'ltr', ar: 'rtl' }
```

## Sequence: Message Loading
```
RootProvider → read cookie → loadMessages(locale) → dynamic import(`./messages/${locale}.json`)
→ on error: fallback to en.json → NextIntlClientProvider wraps app → t() available everywhere
```

## LocaleSwitcher Component
- Renders as a button showing the opposite language name:
  - When `locale === 'ar'`: shows "English" → on click sets `NEXT_LOCALE=en` → reloads
  - When `locale === 'en'`: shows "العربية" → on click sets `NEXT_LOCALE=ar` → reloads
- Used in student layout sidebar and admin layout header bar

## Rules
1. Zero hardcoded user-facing strings — all text uses `t('key')` from next-intl
2. Locale detected from cookie (not URL path, not localStorage)
3. Dynamic RTL/LTR: `<html lang={locale} dir={locale === 'ar' ? 'rtl' : 'ltr'}>`
4. Use CSS logical properties: `ms-`/`me-` (not `ml-`/`mr-`), `ps-`/`pe-`, `border-s-`/`border-e-`
5. `en.json` and `ar.json` must have identical key structures at all times
6. Date formatting via `Intl.DateTimeFormat`, number formatting via `Intl.NumberFormat`
7. Pluralization via next-intl's built-in plural rules

## Examples
- Component: `<p>{t('dashboard.welcome', { name: profile.full_name })}</p>`
- en.json: `"dashboard.welcome": "Welcome back, {name}"`
- ar.json: `"dashboard.welcome": "مرحباً بعودتك، {name}"`
- LocaleSwitcher: `{t('locale.switchTo')}` — renders "English" or "العربية"

## Edge Cases
- Arabic text with embedded English terms → LRE marks (`\u200E`) for correct rendering
- Number formatting: Arabic-Indic numerals (١٢٣) vs Arabic numerals (123)
- Date formats: `DD/MM/YYYY` for Arabic, `MM/DD/YYYY` for English (per locale)
- Plural rules: Arabic has 6 plural forms (zero, one, two, few, many, other) vs English's 2

## Failure Cases
- Missing translation key → renders key name (e.g., `"dashboard.welcome"`)
- Messages file fails to load → fallback to English messages
- New component with hardcoded string → flagged in code review
- Locale cookie unset → defaults to English

## Recovery Procedures
1. Check for missing translation keys by comparing en.json and ar.json
2. Verify every new component uses `t()` — visual scan or lint rule
3. Run `pnpm build` to ensure message imports resolve correctly
4. Test both locales by toggling LocaleSwitcher

## Refactoring Strategy
- Add CI check for matching translation key coverage (en vs ar)
- Move message files to DB-backed storage for admin-editable translations
- Extract locale detection into shared middleware for SSR consistency
- Add automated locale testing in Playwright (AR + EN screenshots)
