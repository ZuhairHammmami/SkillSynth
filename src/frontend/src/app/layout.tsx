import type { Metadata, Viewport } from 'next';
import { Providers } from '@/shared/lib/providers';
import { RootProvider } from '@/i18n/root-provider';
import { Toaster } from '@/shared/ui/sonner';
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
