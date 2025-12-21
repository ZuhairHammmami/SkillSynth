// المسار: src/app/layout.tsx
import type { Metadata } from 'next';
import { Tajawal } from 'next/font/google';
import { Providers } from '@/lib/providers';
import { ClientAppInitializer } from '@/components/ClientAppInitializer';
import { Toaster } from "@/components/ui/sonner";
import { AppLayout } from '@/components/AppLayout';
import './globals.css';

const tajawal = Tajawal({
  subsets: ['arabic'],
  weight: ['400', '500', '700'],
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'SkillSynth',
  description: 'مسار تعلمك، مُصمم خصيصًا لك.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ar" dir="rtl">
      <body className={`${tajawal.className} bg-background text-foreground antialiased`}>
        <Providers>
          <ClientAppInitializer />
          <AppLayout>
            {children}
          </AppLayout>
          <Toaster richColors position="top-center" />
        </Providers>
      </body>
    </html>
  );
}