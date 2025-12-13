// المسار: src/frontend/src/app/layout.tsx
import type { Metadata } from 'next';
import { Tajawal } from 'next/font/google';
import { AuthProvider } from '@/context/AuthContext';
import Header from '@/app/components/Header';
import './globals.css'; // <--- هذا هو السطر الحاسم الذي يستورد كل تصميماتنا

const tajawal = Tajawal({
  subsets: ['arabic'],
  weight: ['400', '500', '700'],
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'SkillSynth',
  description: 'أنشئ مسار تعلمك المخصص والذكي',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.Node;
}>) {
  return (
    <html lang="ar" dir="rtl">
      <body
        className={`${tajawal.className} bg-background text-foreground antialiased`}
      >
        <AuthProvider>
          <div className="relative flex min-h-screen flex-col">
            <Header />
            <main className="flex-grow">{children}</main>
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}