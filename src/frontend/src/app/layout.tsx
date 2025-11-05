// المسار: src/frontend/src/app/layout.tsx

import { Tajawal } from "next/font/google";
import "./globals.css";
import Header from "@/app/components/Header";
import { AuthProvider } from "@/context/AuthContext"; // <-- 1. استيراد المزود

const tajawal = Tajawal({
  subsets: ["arabic"],
  weight: ["400", "700"],
});

export const metadata = {
  title: "SkillSynth",
  description: "أنشئ مسار تعلمك المخصص والذكي",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ar" dir="rtl">
      <body
        className={`${tajawal.className} bg-background text-foreground antialiased`}
      >
        {/* 2. تغليف كل شيء داخل المزود */}
        <AuthProvider>
          <Header />
          <main>{children}</main>
        </AuthProvider>
      </body>
    </html>
  );
}