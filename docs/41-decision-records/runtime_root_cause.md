# Runtime Crash Report — "Event handlers cannot be passed to Client Component props"

## EXACT Source

**File:** `src/frontend/src/app/layout.tsx:33–38`

```tsx
<link
  rel="stylesheet"
  href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap"
  media="print"
  onLoad={(e: any) => { e.target.media = 'all' }}
/>
```

**Component:** `RootLayout` (Server Component, line 18).

**Triggering prop:** `onLoad={(e: any) => { e.target.media = 'all' }}` — a JavaScript function passed as a prop to an intrinsic `<link>` element.

---

## Root Cause Analysis

### The Problem

The root layout (`src/frontend/src/app/layout.tsx`) is a **Server Component** by default in the Next.js App Router. Server Components serialize their output into the RSC (React Server Components) payload — a JSON-based format sent from server to client.

**Functions cannot be serialized to JSON.** When the React server renderer encounters the `onLoad` handler on the `<link>` element, it cannot pass this function to the client, and throws:

```
Error:
Event handlers cannot be passed to Client Component props
<link
media="print"
onLoad={function onLoad}
>
```

### Why It Happens Now

This is a **font loading anti-pattern** carried over from the Pages Router era:

- **Pages Router (`_document.tsx`):** `<link onLoad={...}>` inside `<Head>` worked because `_document.tsx` is a special Next.js construct that renders server-side HTML directly — the `onLoad` became an inline event handler attribute in the static HTML.
- **App Router (`layout.tsx`):** The root layout is a React Server Component. Event handlers are not supported on Server Component-rendered DOM elements because they require client-side JavaScript to execute.

### Build Evidence

```
$ pnpm build
...
./src/app/layout.tsx
28:9  Warning: Custom fonts not added in `pages/_document.js` will only load
       for a single page. This is discouraged.
33:9  Warning: Custom fonts not added in `pages/_document.js` will only load
       for a single page. This is discouraged.
40:11 Warning: Custom fonts not added in `pages/_document.js` will only load
       for a single page. This is discouraged.
```

The `@next/next/no-page-custom-font` lint rule explicitly warns against this pattern. The build completes (React 18 suppresses this as a warning rather than an error), but at **runtime** — especially in development mode (`pnpm dev`) with `reactStrictMode: true` — the error surfaces as a hard crash.

### Why Not `next/font` Is the Missing Piece

The project uses **zero** `next/font` imports:

```
$ grep -rn 'next/font' src/frontend/src/ --include="*.tsx" --include="*.ts"
(no results)
```

Instead, it manually loads Tajawal from Google Fonts with three `<link>` tags (preconnect, preload, stylesheet). The `next/font/google` module exists specifically to eliminate this exact pattern — it handles preconnect, preload, `media="print"` swap, and `onLoad` natively, all correctly within the Server Component model.

---

## How to Fix Properly

### Recommended Fix: Use `next/font/google`

Replace all manual `<link>` tags with `next/font/google`'s `Tajawal` import.

**Changes to `src/frontend/src/app/layout.tsx`:**

```tsx
import type { Metadata, Viewport } from 'next';
import { Providers } from '@/shared/lib/providers';
import { Toaster } from "@/shared/ui/sonner";
import { RootProvider } from '@/i18n/root-provider';
import { cookies } from 'next/headers';
import { Tajawal } from 'next/font/google';
import './globals.css';

const tajawal = Tajawal({
  subsets: ['arabic', 'latin'],
  weight: ['300', '400', '500', '700', '800'],
  display: 'swap',
  variable: '--font-tajawal',
});

export const viewport: Viewport = {
  themeColor: '#ffffff',
};

export const metadata: Metadata = {
  title: 'SkillSynth — Adaptive Learning OS',
  description: 'Personalized learning paths, skill tracking, and analytics for modern professionals.',
  icons: { icon: '/favicon.svg' },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const cookieStore = cookies();
  const locale = cookieStore.get('NEXT_LOCALE')?.value || 'en';
  const dir = locale === 'ar' ? 'rtl' : 'ltr';

  return (
    <html lang={locale} dir={dir} suppressHydrationWarning>
      <body className={`min-h-screen bg-background text-foreground antialiased ${tajawal.variable}`}>
        <RootProvider locale={locale}>
          <Providers>
            {children}
            <Toaster position="top-center" closeButton />
          </Providers>
        </RootProvider>
      </body>
    </html>
  );
}
```

Then in `tailwind.config.js`, map the CSS variable to `fontFamily`:

```js
fontFamily: {
  sans: ['var(--font-tajawal)', 'Tajawal', 'sans-serif'],
},
```

### Benefits

| Concern | Manual `<link>` | `next/font/google` |
|---------|-----------------|---------------------|
| Server Component compatible | ❌ | ✅ |
| Automatic preconnect | Manual | ✅ Built-in |
| Automatic preload | Manual | ✅ Built-in |
| `media="print"` swap | Manual `onLoad` hack | ✅ Automatic |
| No FOUT/FOIT | Depends on `onLoad` timing | ✅ `display=swap` |
| No runtime error | ❌ | ✅ |
| No ESLint warnings | ❌ | ✅ |
| CSS variable for Tailwind | Manual | ✅ Automatic |
| Self-hosts font file | ❌ (CDN dependency) | ✅ (optional `downloadable`) |

### Fallback Fix (if `next/font` is undesirable)

If for some reason `next/font` cannot be used, extract the problematic `<link>` into a Client Component:

```tsx
// src/frontend/src/shared/ui/font-loader.tsx
'use client';

import { useEffect } from 'react';

export function FontLoader() {
  useEffect(() => {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap';
    document.head.appendChild(link);
  }, []);
  return null;
}
```

Then in `layout.tsx`: replace the `<link onLoad={...}>` with `<FontLoader />`.

---

## Summary

| Item | Detail |
|------|--------|
| **File** | `src/frontend/src/app/layout.tsx` |
| **Lines** | 33–38 |
| **Culprit** | `<link media="print" onLoad={(e) => { e.target.media = 'all' }} />` |
| **Root Cause** | Event handler function passed in a Server Component — cannot be serialized to RSC payload |
| **Fix** | Replace manual Google Fonts `<link>` tags with `next/font/google`'s `Tajawal` import |
