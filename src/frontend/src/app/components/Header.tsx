// المسار: src/frontend/src/app/components/Header.tsx
'use client';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/context/AuthContext';

export default function Header() {
  const { isAuthenticated, logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    <header className="bg-background sticky top-0 z-50 w-full border-b">
      <nav className="container mx-auto px-4 sm:px-6 lg:px-8 py-3 flex justify-between items-center">
        <Link href="/" className="text-xl font-bold text-primary">
          SkillSynth
        </Link>
        <div className="flex items-center gap-4">
          {isAuthenticated ? (
            <>
              {/* رسالة ترحيب عامة */}
              <span className="text-sm font-medium text-foreground hidden sm:inline">
                مرحباً بك
              </span>
              <Button onClick={handleLogout} variant="outline">
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