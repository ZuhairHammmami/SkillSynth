import type { Metadata } from 'next';
import { Tajawal } from 'next/font/google';
import { Providers } from '@/lib/providers';
import { ClientAppInitializer } from '@/components/ClientAppInitializer';
import { Toaster } from "@/components/ui/sonner";
import { AppLayout } from '@/components/AppLayout';
import { AnimatedBackground } from '@/components/AnimatedBackground';
import './globals.css';

// إعداد خط تجوال العربي
const tajawal = Tajawal({
  subsets: ['arabic'],
  weight: ['400', '500', '700'],
  display: 'swap',
});

// إعدادات الميتاداتا (العنوان والوصف)
export const metadata: Metadata = {
  title: 'SkillSynth - مسار تعلمك الذكي',
  description: 'منصة ذكية لبناء مسارات تعلم مخصصة باستخدام الذكاء الاصطناعي.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ar" dir="rtl">
      <body className={`${tajawal.className} min-h-screen bg-background text-foreground antialiased selection:bg-primary/20 selection:text-primary`}>
        <Providers>
          {/* مهيئ التطبيق (للتحقق من التوكن عند البدء) */}
          <ClientAppInitializer />
          
          {/* الخلفية المتحركة (تكون في الخلفية تماماً بفضل z-index السالب داخلها) */}
          <AnimatedBackground />
          
          {/* تخطيط التطبيق الذي يدير الهيدر والمحتوى */}
          <AppLayout>
            {children}
          </AppLayout>
          
          {/* مكون التنبيهات المنبثقة */}
          <Toaster richColors position="top-center" closeButton />
        </Providers>
      </body>
    </html>
  );
}