// المسار: src/app/layout.tsx

import type { Metadata } from 'next';
import { Tajawal } from 'next/font/google';
import { AuthProvider } from '@/context/AuthContext';
import Header from '@/app/components/Header';
import { Toaster } from "@/components/ui/sonner";
import { AnimatedBackground } from '@/app/components/AnimatedBackground';
import './globals.css';

// إعداد الخط المخصص (Tajawal) مع مجموعة الحروف العربية
const tajawal = Tajawal({
  subsets: ['arabic'],
  weight: ['400', '500', '700'],
  display: 'swap', // يضمن عرض النص بخط احتياطي حتى يتم تحميل الخط المخصص
  variable: '--font-tajawal', // لسهولة الاستخدام في المستقبل إذا احتجناه
});

export const metadata: Metadata = {
  title: 'SkillSynth',
  description: 'حوّل أهدافك إلى خطة عمل واضحة وفعالة. مسار تعلمك، مُصمم خصيصًا لك.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ar" dir="rtl">
      <body
        className={`${tajawal.className} bg-background text-foreground antialiased`}
      >
        <AuthProvider>
          <div className="relative flex min-h-screen flex-col">
            {/* الخلفية المتحركة التي ستعمل تحت كل المحتوى */}
            <AnimatedBackground />

            {/* الشريط العلوي */}
            <Header />

            {/* المحتوى الرئيسي الديناميكي لكل صفحة */}
            <main className="flex-grow z-10">{children}</main>

            {/* نظام الإشعارات (Toaster) */}
            <Toaster richColors position="top-center" />
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}