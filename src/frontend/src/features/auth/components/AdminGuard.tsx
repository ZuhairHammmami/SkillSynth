// src/features/auth/components/AdminGuard.tsx
'use client';

import { useAuthStore } from '@/shared/store/authStore';
import { useUser } from '@/features/user/hooks/useUser';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Skeleton } from '@/shared/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/shared/ui/alert';
import { AlertCircle } from 'lucide-react';

export const AdminGuard = ({ children }: { children: React.ReactNode }) => {
  // Session state from Zustand
  const { isAuthenticated, isLoading: isSessionLoading } = useAuthStore();
  
  // User data from React Query
  const { user, isLoading: isUserLoading } = useUser();
  
  const router = useRouter();

  const isLoading = isSessionLoading || isUserLoading;

  useEffect(() => {
    // Wait for initial user verification to complete
    if (!isLoading) {
      // If not authenticated, redirect to login
      if (!isAuthenticated) {
        router.push('/login');
      } 
      // If authenticated but not admin, redirect to user dashboard
      else if (user && !user.is_admin) {
        router.push('/dashboard');
      }
    }
  }, [isAuthenticated, isLoading, user, router]);

  // Show loading skeleton during verification
  if (isLoading) {
    return (
        <div className="container mx-auto p-8 space-y-4">
            <Skeleton className="h-12 w-1/3" />
            <Skeleton className="h-64 w-full" />
        </div>
    );
  }
  
  // Show content if authenticated and is admin
  if (isAuthenticated && user?.is_admin) {
      return <>{children}</>;
  }

  // Show error message temporarily before redirect
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