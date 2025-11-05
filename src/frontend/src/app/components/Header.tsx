// المسار: src/frontend/src/app/components/Header.tsx
'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/context/AuthContext'; // <-- استيراد الدماغ

export default function Header() {
  const { user, isAuthenticated, logout } = useAuth(); // <-- استخدام بيانات المستخدم

  return (
    <header className="bg-background sticky top-0 z-50 w-full border-b">
      <nav className="container mx-auto px-6 py-3 flex justify-between items-center">
        <Link href="/" className="text-xl font-bold text-primary">
          SkillSynth
        </Link>
        <div className="flex items-center gap-4">
          {isAuthenticated && user ? (
            <>
              <span className="text-foreground">مرحباً، {user.full_name}</span>
              <Button onClick={logout} variant="ghost">
                تسجيل الخروج
              </Button>
            </>
          ) : (
            <Button asChild>
              <Link href="/login">تسجيل الدخول</Link>
            </Button>
          )}
        </div>
      </nav>
    </header>
  );
}