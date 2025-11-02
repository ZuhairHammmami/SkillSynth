// app/layout.tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Header from '@/app/components/Header'; // استيراد المكون

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "SkillSynth",
  description: "AI-Powered Learning Path Generator",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ar" dir="rtl">
      <body className={inter.className}>
        <Header userName="مستخدم جديد" /> {/* استخدام المكون */}
        {children}
      </body>
    </html>
  );
}