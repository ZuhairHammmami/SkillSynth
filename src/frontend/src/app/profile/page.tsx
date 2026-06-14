// src/app/profile/page.tsx
'use client';
import { useUser } from '@/features/user/hooks/useUser';
import { AuthGuard } from '@/features/auth/components/AuthGuard';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card';
import { UpdateProfileForm } from '@/features/user/components/UpdateProfileForm';
import { ChangePasswordForm } from '@/features/user/components/ChangePasswordForm';
import { Skeleton } from '@/shared/ui/skeleton';

function ProfileContent() {
  // User data from React Query
  const { user, isLoading, isError } = useUser();

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (isError || !user) {
    return (
      <div className="text-center py-10">
        <p className="text-muted-foreground">خطأ في تحميل بيانات الملف الشخصي</p>
      </div>
    );
  }

  return (
    <Tabs defaultValue="profile">
      <TabsList className="grid w-full grid-cols-2">
        <TabsTrigger value="profile">الملف الشخصي</TabsTrigger>
        <TabsTrigger value="password">الأمان</TabsTrigger>
      </TabsList>
      <TabsContent value="profile" className="mt-4">
        <Card>
          <CardHeader>
            <CardTitle>الملف الشخصي</CardTitle>
            <CardDescription>تحديث معلومات حسابك.</CardDescription>
          </CardHeader>
          <CardContent>
            <UpdateProfileForm user={user} />
          </CardContent>
        </Card>
      </TabsContent>
      <TabsContent value="password" className="mt-4">
        <Card>
          <CardHeader>
            <CardTitle>تغيير كلمة المرور</CardTitle>
            <CardDescription>اختر كلمة مرور جديدة وقوية.</CardDescription>
          </CardHeader>
          <CardContent>
            <ChangePasswordForm />
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  );
}

export default function ProfilePage() {
    return (
        <AuthGuard>
            <div className="container mx-auto py-10 max-w-2xl">
                <ProfileContent />
            </div>
        </AuthGuard>
    );
}