// المسار: src/features/auth/components/AdminGuard.tsx
'use client';
import { useAuthStore } from '@/store/authStore';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export const AdminGuard = ({ children }: { children: React.ReactNode }) => {
  const { user, isAuthenticated, isLoading } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated) {
        router.push('/login'); // غير مسجل دخوله
      } else if (!user?.is_admin) {
        router.push('/dashboard'); // ليس أدمن
      }
    }
  }, [isAuthenticated, isLoading, user, router]);

  // اعرض شاشة تحميل أثناء التحقق
  if (isLoading || !isAuthenticated || !user?.is_admin) {
    return <div className="text-center p-10">⏳ جارٍ التحقق من الصلاحيات...</div>;
  }
  
  // إذا كان أدمن، اعرض المحتوى
  return <>{children}</>;
};