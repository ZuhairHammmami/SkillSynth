// المسار: src/features/auth/components/AuthGuard.tsx
'use client';
import { useAuthStore } from '@/shared/store/authStore';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Skeleton } from '@/shared/ui/skeleton';

export const AuthGuard = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="container mx-auto p-8 space-y-4">
        <Skeleton className="h-10 w-1/4" />
        <div className="grid gap-6 md:grid-cols-3">
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-32 w-full" />
        </div>
      </div>
    );
  }
  
  if (isAuthenticated) {
      return <>{children}</>;
  }

  return null;
};