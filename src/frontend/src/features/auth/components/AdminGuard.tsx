// المسار: src/features/auth/components/AdminGuard.tsx
'use client';

import { useAuthStore } from '@/store/authStore';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';

export const AdminGuard = ({ children }: { children: React.ReactNode }) => {
  const { user, isAuthenticated, isLoading } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    // انتظر حتى تنتهي عملية التحقق الأولية من المستخدم
    if (!isLoading) {
      // إذا لم يكن مسجلاً دخوله، أعد توجيهه لصفحة الدخول
      if (!isAuthenticated) {
        router.push('/login');
      } 
      // إذا كان مسجلاً دخوله لكنه ليس أدمن، أعد توجيهه للوحة تحكم المستخدم
      else if (user && !user.is_admin) {
        router.push('/dashboard');
      }
    }
  }, [isAuthenticated, isLoading, user, router]);

  // أثناء التحقق من المستخدم، اعرض شاشة تحميل احترافية
  if (isLoading) {
    return (
        <div className="container mx-auto p-8 space-y-4">
            <Skeleton className="h-12 w-1/3" />
            <Skeleton className="h-64 w-full" />
        </div>
    );
  }
  
  // إذا كان المستخدم مسجلاً دخوله وهو أدمن، اعرض المحتوى المحمي
  if (isAuthenticated && user?.is_admin) {
      return <>{children}</>;
  }

  // في حالة عدم تحقق الشروط، اعرض رسالة خطأ مؤقتة قبل إعادة التوجيه
  return (
    <div className="container mx-auto p-8">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>وصول مرفوض</AlertTitle>
          <AlertDescription>
            ليس لديك الصلاحيات اللازمة للوصول إلى هذه الصفحة. سيتم إعادة توجيهك الآن.
          </AlertDescription>
        </Alert>
    </div>
  );
};