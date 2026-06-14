import type { Metadata } from 'next';
import { Providers } from '@/shared/lib/providers';
import { ClientAppInitializer } from '@/shared/components/ClientAppInitializer';
import { Toaster } from "@/shared/ui/sonner";
import { AppLayout } from '@/shared/components/AppLayout';
import { AnimatedBackground } from '@/shared/components/AnimatedBackground';
import './globals.css';

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
      <body className="min-h-screen bg-background text-foreground antialiased selection:bg-primary/20 selection:text-primary">
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