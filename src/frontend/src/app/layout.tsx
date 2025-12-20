// المسار: src/app/layout.tsx
import type { Metadata } from 'next';
import { Tajawal } from 'next/font/google';
import { Providers } from '@/lib/providers';
import Header from '@/components/Header';
import { Toaster } from "@/components/ui/sonner";
import { AnimatedBackground } from '@/components/AnimatedBackground';
import { ClientAppInitializer } from '@/components/ClientAppInitializer'; // <-- استيراد المكون الجديد
import './globals.css';

const tajawal = Tajawal({
  subsets: ['arabic'],
  weight: ['400', '500', '700'], // <-- تمت إعادة السطر المفقود
  display: 'swap',
  variable: '--font-tajawal',
});
export const metadata: Metadata = { /* ... */ };

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ar" dir="rtl">
      <body className={`${tajawal.className} bg-background text-foreground antialiased`}>
        <Providers>
          <ClientAppInitializer /> {/* <-- إضافة المكون هنا */}
          <div className="relative flex min-h-screen flex-col">
            <AnimatedBackground />
            <Header />
            <main className="flex-grow z-10">{children}</main>
            <Toaster richColors position="top-center" />
          </div>
        </Providers>
      </body>
    </html>
  );
}