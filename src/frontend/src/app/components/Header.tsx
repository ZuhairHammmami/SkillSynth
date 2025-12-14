'use client';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/context/AuthContext';
import { Logo } from './Logo'; // <-- استيراد الشعار

export default function Header() {
  const { isAuthenticated, logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    <header className="bg-background/80 backdrop-blur-sm sticky top-0 z-50 w-full border-b">
      <nav className="container mx-auto px-4 sm:px-6 lg:px-8 py-3 flex justify-between items-center">
        <Link href="/">
          <Logo />
        </Link>
        <div className="flex items-center gap-2">
          {isAuthenticated ? (
            <>
              <Button onClick={() => router.push('/dashboard')} variant="ghost">لوحة التحكم</Button>
              <Button onClick={handleLogout}>تسجيل الخروج</Button>
            </>
          ) : (
            <>
                <Button asChild variant="ghost">
                    <Link href="/login">تسجيل الدخول</Link>
                </Button>
                <Button asChild>
                    <Link href="/register">أنشئ حسابًا</Link>
                </Button>
            </>
          )}
        </div>
      </nav>
    </header>
  );
}